-- ============================================================================
-- Wajhatna Riyadh AI Decision Support Platform
-- FINAL LOCKED PRODUCTION SCHEMA
-- 9 canonical tables. No transit_route_stops. No stored spatial/temporal FKs
-- for POIs/Events/Holidays/Prayer_Times. metro_stations has NO geom (Option A).
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS postgis;

-- ============================================================================
-- 1. METRO_LINES
-- ============================================================================
CREATE TABLE metro_lines (
    line_number       TEXT PRIMARY KEY,
    line_name         TEXT NOT NULL,
    line_color_hex    TEXT,
    terminal_stations TEXT,
    geom              geometry(LineString, 4326) NOT NULL,
    source            TEXT NOT NULL,
    retrieved_at      TIMESTAMPTZ NOT NULL
);
CREATE INDEX idx_metro_lines_geom ON metro_lines USING GIST (geom);

-- ============================================================================
-- 2. METRO_STATIONS  -- Identity only. NO geom (locked decision, Option A).
-- ============================================================================
CREATE TABLE metro_stations (
    station_id                TEXT PRIMARY KEY,
    station_name_ar           TEXT NOT NULL,
    station_name_en           TEXT NOT NULL,
    coord_valid                BOOLEAN DEFAULT TRUE,
    name_en_review_required    BOOLEAN DEFAULT FALSE,
    name_review_note           TEXT,
    is_interchange              BOOLEAN NOT NULL,
    source                       TEXT NOT NULL,
    retrieved_at                  TIMESTAMPTZ NOT NULL
);
COMMENT ON TABLE metro_stations IS 'Station IDENTITY only. Authoritative geometry lives in metro_station_lines - interchange stations have DIFFERENT coordinates per line (verified). Use metro_stations_with_representative_geom VIEW if a single point per station is needed.';
COMMENT ON COLUMN metro_stations.is_interchange IS 'DERIVED from metro_station_lines (station appears on >1 line). Recompute via refresh_derived_metro_flags() after any metro_station_lines change.';

-- ============================================================================
-- 3. METRO_STATION_LINES  -- AUTHORITATIVE platform geometry
-- ============================================================================
CREATE TABLE metro_station_lines (
    station_id                TEXT NOT NULL REFERENCES metro_stations(station_id),
    line_number                TEXT NOT NULL REFERENCES metro_lines(line_number),
    station_type                TEXT,
    sequence_on_line             INTEGER,
    geom                          geometry(Point, 4326) NOT NULL,
    spatial_review_required       BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (station_id, line_number),
    CONSTRAINT chk_riyadh_bounds CHECK (
        ST_Y(geom) BETWEEN 24.0 AND 25.3 AND ST_X(geom) BETWEEN 46.0 AND 47.3
    )
);
CREATE INDEX idx_metro_station_lines_geom ON metro_station_lines USING GIST (geom);
CREATE INDEX idx_metro_station_lines_line ON metro_station_lines (line_number);
COMMENT ON TABLE metro_station_lines IS 'AUTHORITATIVE per-line platform coordinates. 94 rows = 1:1 with original source Metro_Stations rows.';
COMMENT ON COLUMN metro_station_lines.station_type IS 'Can legitimately differ per line for the same physical station (verified: station S32 differs between lines).';

CREATE OR REPLACE FUNCTION refresh_derived_metro_flags() RETURNS void AS $$
BEGIN
    UPDATE metro_stations ms
    SET is_interchange = (
        SELECT COUNT(*) > 1 FROM metro_station_lines msl WHERE msl.station_id = ms.station_id
    );
END;
$$ LANGUAGE plpgsql;

CREATE VIEW metro_stations_with_representative_geom AS
SELECT ms.*,
    (SELECT ST_SetSRID(ST_MakePoint(AVG(ST_X(msl.geom)), AVG(ST_Y(msl.geom))), 4326)
     FROM metro_station_lines msl WHERE msl.station_id = ms.station_id) AS representative_geom
FROM metro_stations ms;
COMMENT ON VIEW metro_stations_with_representative_geom IS 'DERIVED representative point (centroid of per-line platforms). NOT authoritative. Use metro_station_lines.geom for precise per-line queries.';

-- ============================================================================
-- 4. BUS_STOPS
-- ============================================================================
CREATE TABLE bus_stops (
    stop_id            BIGINT PRIMARY KEY,
    stop_name          TEXT NOT NULL,
    shelter_type_code  TEXT,
    shelter_type       TEXT,
    bus_line_code      TEXT,
    bus_line_number    INTEGER,
    direction          SMALLINT CHECK (direction IN (1,2)),
    sequence_on_line   INTEGER,
    development_stage  TEXT,
    geom               geometry(Point, 4326) NOT NULL,
    source             TEXT NOT NULL,
    retrieved_at       TIMESTAMPTZ NOT NULL,
    coord_valid         BOOLEAN DEFAULT TRUE,
    spatial_review_required BOOLEAN DEFAULT FALSE
);
CREATE INDEX idx_bus_stops_geom ON bus_stops USING GIST (geom);
CREATE INDEX idx_bus_stops_line_dir ON bus_stops (bus_line_number, direction);

-- ============================================================================
-- 5. TRANSIT_ROUTES
-- ============================================================================
CREATE TABLE transit_routes (
    route_id                    TEXT PRIMARY KEY,
    bus_line_number             INTEGER NOT NULL,
    direction                   SMALLINT NOT NULL CHECK (direction IN (1,2)),
    origin                      TEXT,
    destination                 TEXT,
    origin_destination_status   TEXT,
    geom                        geometry(LineString, 4326) NOT NULL,
    source                      TEXT NOT NULL,
    retrieved_at                TIMESTAMPTZ NOT NULL,
    spatial_review_required     BOOLEAN DEFAULT FALSE,
    UNIQUE (bus_line_number, direction)
);
CREATE INDEX idx_transit_routes_geom ON transit_routes USING GIST (geom);
COMMENT ON TABLE transit_routes IS 'bus_stops relates to this table via LOGICAL join on (bus_line_number, direction), verified 1:N - no physical FK, no transit_route_stops junction.';

-- ============================================================================
-- 6. EVENTS
-- ============================================================================
CREATE TABLE events (
    event_id                     TEXT PRIMARY KEY,
    event_name                   TEXT NOT NULL,
    event_type                   TEXT,
    venue_name                   TEXT,
    geom                          geometry(Point, 4326) NOT NULL,
    start_date                    DATE NOT NULL,
    end_date                      DATE NOT NULL,
    opening_time                    TIME,
    closing_time                    TIME,
    coordinate_source                TEXT,
    coordinate_source_confidence      TEXT,
    outside_typical_riyadh_urban_core BOOLEAN DEFAULT FALSE,
    source                             TEXT NOT NULL,
    retrieved_at                        TIMESTAMPTZ NOT NULL,
    CONSTRAINT chk_event_date_order CHECK (end_date >= start_date)
);
CREATE INDEX idx_events_geom ON events USING GIST (geom);
CREATE INDEX idx_events_dates ON events (start_date, end_date);

CREATE VIEW events_live_status AS
SELECT *,
    CASE
        WHEN CURRENT_DATE < start_date THEN 'Upcoming'
        WHEN CURRENT_DATE BETWEEN start_date AND end_date THEN 'Active'
        ELSE 'Past'
    END AS event_status
FROM events;
COMMENT ON VIEW events_live_status IS 'Computed at query time via CURRENT_DATE. Never store event_status as a physical column.';

CREATE VIEW events_with_nearest_transit AS
SELECT e.*,
    (SELECT msl.station_id FROM metro_station_lines msl ORDER BY msl.geom <-> e.geom LIMIT 1) AS nearest_metro_station_id,
    (SELECT ST_Distance(msl.geom::geography, e.geom::geography) FROM metro_station_lines msl ORDER BY msl.geom <-> e.geom LIMIT 1) AS nearest_metro_distance_m,
    (SELECT bs.stop_id FROM bus_stops bs ORDER BY bs.geom <-> e.geom LIMIT 1) AS nearest_bus_stop_id,
    (SELECT ST_Distance(bs.geom::geography, e.geom::geography) FROM bus_stops bs ORDER BY bs.geom <-> e.geom LIMIT 1) AS nearest_bus_distance_m
FROM events e;
COMMENT ON VIEW events_with_nearest_transit IS 'Computed live via PostGIS KNN (<->) at query time. Never store as a snapshot column.';

-- ============================================================================
-- 7. SAUDI_HOLIDAYS
-- ============================================================================
CREATE TABLE saudi_holidays (
    holiday_id     TEXT PRIMARY KEY,
    holiday_name   TEXT NOT NULL,
    holiday_type   TEXT,
    start_date     DATE NOT NULL,
    end_date       DATE NOT NULL,
    date_status    TEXT NOT NULL,
    confidence     TEXT,
    source         TEXT NOT NULL,
    retrieved_at   TIMESTAMPTZ NOT NULL,
    CONSTRAINT chk_holiday_date_order CHECK (end_date >= start_date)
);
CREATE INDEX idx_holidays_dates ON saudi_holidays (start_date, end_date);

-- ============================================================================
-- 8. PRAYER_TIMES  -- PK = date only
-- ============================================================================
CREATE TABLE prayer_times (
    date                DATE PRIMARY KEY,
    hijri_date          TEXT,
    location            TEXT,
    latitude             DOUBLE PRECISION,
    longitude             DOUBLE PRECISION,
    timezone               TEXT DEFAULT 'Asia/Riyadh',
    fajr                     TIME NOT NULL,
    sunrise                   TIME NOT NULL,
    dhuhr                      TIME NOT NULL,
    asr                         TIME NOT NULL,
    maghrib                      TIME NOT NULL,
    isha                          TIME NOT NULL,
    calculation_method              TEXT NOT NULL,
    data_status                      TEXT DEFAULT 'Calculated',
    source                            TEXT NOT NULL,
    retrieved_at                       TIMESTAMPTZ NOT NULL,
    CONSTRAINT chk_coverage CHECK (date BETWEEN '2026-08-01' AND '2026-09-30')
);
CREATE INDEX idx_prayer_times_date ON prayer_times (date);

-- ============================================================================
-- 9. POIS
-- ============================================================================
CREATE TABLE pois (
    poi_id                      TEXT PRIMARY KEY,
    name                        TEXT,
    name_en                     TEXT,
    type                        TEXT NOT NULL,
    subtype                     TEXT,
    opening_hours               TEXT,
    latitude                    DOUBLE PRECISION NOT NULL,
    longitude                   DOUBLE PRECISION NOT NULL,
    geom                        geometry(Point, 4326)
                                 GENERATED ALWAYS AS (ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)) STORED,
    name_original                TEXT,
    name_status                  TEXT NOT NULL,
    name_source                  TEXT,
    name_confidence               TEXT,
    name_en_status                TEXT NOT NULL,
    opening_hours_source          TEXT,
    opening_hours_status          TEXT NOT NULL,
    opening_hours_confidence      TEXT,
    review_required               BOOLEAN NOT NULL DEFAULT FALSE,
    review_priority                TEXT,
    review_reason                  TEXT,
    source_layer                    TEXT NOT NULL,
    source_id                       TEXT NOT NULL
);
CREATE INDEX idx_pois_geom ON pois USING GIST (geom);
CREATE INDEX idx_pois_type ON pois (type);
CREATE VIEW pois_verified AS SELECT * FROM pois WHERE review_required = FALSE;
COMMENT ON COLUMN pois.type IS 'Source contains the typo "Mousque" for all 2074 mosque records. Preserved verbatim per locked governance decision - see README_METADATA.';

-- ============================================================================
-- RELATIONSHIP POLICY SUMMARY
-- Physical FKs (2 only):
--   metro_station_lines.station_id -> metro_stations.station_id
--   metro_station_lines.line_number -> metro_lines.line_number
-- Logical/analytical join (not FK):
--   bus_stops.(bus_line_number, direction) <-> transit_routes.(bus_line_number, direction)
-- Spatial query-time only (no FK, no stored column):
--   pois <-> metro_stations / bus_stops
--   events <-> metro_stations / bus_stops  (see events_with_nearest_transit VIEW)
-- Temporal query-time only (no FK):
--   events <-> saudi_holidays (date range overlap)
--   events <-> prayer_times (exact date match)
-- Explicitly removed / never created:
--   transit_route_stops, metro_lines<->events, metro_station_lines<->events,
--   metro_stations.geom (Option A locked decision)
-- ============================================================================
