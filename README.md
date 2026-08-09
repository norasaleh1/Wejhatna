# Riyadh AI Decision Support Platform

An AI-powered decision support platform for Riyadh that combines spatial data, geospatial analysis, real-world APIs, and an AI Agent to provide context-aware recommendations and insights.

## Project Overview

The **Riyadh AI Decision Support Platform** is designed to support smarter decisions by combining structured city data with spatial intelligence and AI reasoning.

Instead of relying only on static information, the platform can use location-based data, spatial queries, external APIs, and AI tool calling to analyze real-world conditions and generate useful recommendations.

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
5. Tool Calling connects the agent to spatial queries, maps, weather, and other services.
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
        /    |     \
       /     |      \
Spatial   Google   Weather
Analysis   Maps      API
       \     |      /
        \    |     /
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

## Data Policy

The full **Master Data** is intentionally not stored in this public repository.

Only one or more of the following should be committed:

- Small sample datasets
- Processed sample data
- Database schema files
- Data preparation scripts
- Documentation describing the original data source and preparation process

This keeps the repository lightweight and helps respect possible data access, licensing, and privacy restrictions.

## Security

Sensitive information must **never** be committed to this repository.

Do not commit:

- `.env`
- API keys
- Database passwords
- Service-account credentials
- Access tokens
- Private certificates
- Production connection strings
- Sensitive or restricted datasets

Use environment variables locally and document required variables in `.env.example` using placeholder values only.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/riyadh-ai-decision-support-platform.git
cd riyadh-ai-decision-support-platform
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Copy:

```text
.env.example
```

to:

```text
.env
```

Then add your local credentials to `.env`.

**Never commit the `.env` file.**

## Project Status

🚧 **Work in Progress**

This repository is being developed incrementally. Components, datasets, APIs, tools, and documentation will be added and updated as the project progresses.

## Future Development

Possible next steps include:

- PostgreSQL/PostGIS database initialization
- Spatial data ingestion and preprocessing
- Spatial analysis tools
- Backend API endpoints
- AI Agent implementation
- Google Maps integration
- Weather API integration
- Tool Calling workflows
- Frontend dashboard
- Architecture diagrams and technical documentation

## Team

Developed as part of the **Riyadh AI Decision Support Platform** project.
