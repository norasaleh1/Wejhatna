<p align="center">
  <img src="docs/Wejhatna.png" width="100%" alt="Riyadh AI Decision Support Platform">
</p>

# Wejhatna : Riyadh AI Decision Support Platform

An AI-powered decision support platform for Riyadh that combines spatial data, geospatial analysis, real-world APIs, and an AI Agent to provide context-aware recommendations and insights.

## Project Overview

The **Wejhatna** is designed to support smarter decisions by combining structured city data with spatial intelligence and AI reasoning.

Instead of relying only on static information, the platform can use location-based data, spatial queries, external APIs, weather conditions, prayer times, and AI tool calling to analyze real-world conditions and generate useful recommendations.

## Problem

Urban decision-making often requires information from multiple disconnected sources, such as:

- Geographic and spatial data
- Points of interest and city infrastructure
- Weather conditions
- Maps and travel information
- Structured datasets
- User-specific queries and requirements

Analyzing these sources manually can be slow and difficult, especially when spatial relationships and changing external conditions need to be considered.

## Solution

The platform creates a unified decision-support layer where:

1. Data is collected, cleaned, and prepared.
2. Structured and spatial data is stored in **PostgreSQL + PostGIS**.
3. An **API / Data Layer** exposes safe and structured access to the data.
4. An **AI Agent** interprets user requests and selects the appropriate tools.
5. Tool Calling connects the agent to spatial queries, Google Maps, weather information, prayer times, and other external services.
6. A frontend presents the final analysis and recommendations to the user.

## Architecture

```text
        Data Sources
             |
             v
   PostgreSQL + PostGIS
             |
             v
      API / Data Layer
             |
             v
          AI Agent
      /      |       \
     /       |        \
Spatial   External    Prayer
Analysis    APIs      Times
           /   \
     Google     Weather
      Maps        API
             |
             v
          Frontend
```

Simplified flow:

```text
Data → PostgreSQL/PostGIS → API/Data Layer → AI Agent → Frontend
```

## Core Technologies

- **PostgreSQL** — relational database
- **PostGIS** — geospatial database extension
- **Spatial Analysis** — geographic queries and location-based analysis
- **AI Agent** — reasoning and decision-support layer
- **Tool Calling** — allows the AI Agent to call platform tools and APIs
- **Google Maps** — mapping, places, routing, and location information
- **Weather API** — real-time or forecast weather information
- **Python** — backend, data processing, and agent development

Additional technologies may be added as the project evolves.

## Repository Structure

```text
riyadh-ai-decision-support-platform/
│
├── agent/
│   ├── tools/
│   └── README.md
│
├── backend/
│   └── README.md
│
├── database/
│   ├── schema/
│   ├── sample_data/
│   └── README.md
│
├── frontend/
│   └── README.md
│
├── docs/
│   └── README.md
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```


## Team

Developed by:

- Nora Alkhudar
- Aryam Alsaidi
- Shahad Alrashidi
- Jowaher
