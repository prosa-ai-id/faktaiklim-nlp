<div align="center">
<p>
  <img src="images/logo.png" alt="Logo FaktaIklim">
</p>
</div>

# FaktaIklim Climate API

FaktaIklim Climate API is a service that provides endpoints for classifying climate-related topics, verifying text for hoaxes, and managing articles in climate-related collections. This API helps combat misinformation by providing tools for fact-checking and content classification.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [API Reference](#api-reference)
  - [Topic Classification](#topic-classification)
  - [Text Verification](#text-verification)
  - [Article Management](#article-management)
  - [Collection Management](#collection-management)
  - [System Status](#system-status)

## Prerequisites

- [uv package manager](https://docs.astral.sh/uv/)

## Setup

1. Install dependencies:
    ```bash
    uv sync
    ```

2. Start the application:
    ```bash
    uv run fastapi run
    ```

## API Reference

### Topic Classification

#### Predict Topic and Subtopic
Analyzes text to predict its climate-related topic and subtopic.

**Endpoint:** `POST /topic`

**Request Body:**
```json
{
    "text": "TOPIK ARTIKEL:\nkebijakan dan pemerintahan\nkonservasi lingkungan\nTEKS BERITA:\nProvinsi Gorontalo masuk dalam Program Laut Sejahtera..."
}
```

**Response:**
```json
{
    "result": {
        "topic": {
            "konservasi lingkungan": 0.886
        },
        "subtopic": {
            "peran pemerintah lokal": 0.812
        }
    }
}
```

### Text Verification

#### Check Text Veracity
Analyzes text to determine if it contains factual or misleading climate-related information.

**Endpoint:** `POST /check`

**Request Body:**
```json
{
    "text": "TOPIK ARTIKEL:\nkebijakan dan pemerintahan\nkonservasi lingkungan\nTEKS BERITA:\nProvinsi Gorontalo masuk dalam Program Laut Sejahtera..."
}
```

**Response:**
```json
{
    "relevant_items": [
        {
            "title": "Eropa dilanda pemadaman listrik...",
            "content": "Brussel (ANTARA) - Gelombang panas...",
            "url": "https://www.antaranews.com/berita/4226195/eropa-dilanda-pemadaman-listrik...",
            "score": 0.658,
            "stance": "support",
            "hoax_status": "fact"
        }
    ],
    "hoax_probability": 0.5
}
```

### Article Management

#### Insert or Update Article
Creates or updates an article in the climate hoax collection.

**Endpoint:** `PUT /article/<item_id>`

**Request Body:**
```json
{
    "id": 19206,
    "title": "Akun Instagram Mengatasnamakan Rumah Sakit Hermina",
    "content": "Beredar sebuah informasi bahwa lantai tiga Rumah Sakit..",
    "html_content": "Beredar sebuah informasi bahwa lantai tiga Rumah Sakit..",
    "short_content": "Beredar sebuah informasi bahwa lantai tiga Rumah Sakit..",
    "created_by": "Dedy",
    "localtime": "2022-12-21 07:50:56",
    "publish_localtime": null,
    "user_publish_date": "2022-12-14 07:00:00",
    "stamped_image_url": [
        "/media/images/issue/17f79afc-8ddc-4111-b82f-bc0756492641.png"
    ],
    "classification": "HOAKS",
    "category": "Disasters and Accidents",
    "status_name": "submitted",
    "status_reason": "empty",
    "status_created_by": "Dedy",
    "status_localtime": "2022-12-21 07:50:56",
    "tags": [
        "gempa",
        "karangasem"
    ],
    "verify_url": [],
    "distributions": [],
    "source_description": "https://www.youtube.com/shorts/2c_zICAym7U"
}
```

**Response:**
```json
{
    "status": "item id 19206 is inserted into climate_hoax"
}
```

#### Delete Article
Removes an article from both climate_hoax and climate_fact collections.

**Endpoint:** `DELETE /article/<item_id>`

**Response:**
```json
{
    "status": "item id 19206 is deleted from [climate_hoax, climate_fact]"
}
```

### Collection Management

#### Get Article Collections
Retrieves information about all available collections.

**Endpoint:** `GET /collections`

**Response:**
```json
{
    "result": [
        {
            "id": "climate_fact",
            "name": "Climate_Fact",
            "documents_count": 4
        },
        {
            "id": "climate_hoax",
            "name": "Climate_Hoax",
            "documents_count": 5
        }
    ]
}
```

### System Status

#### Health Check
Verifies the API's operational status.

**Endpoint:** `GET /healthcheck`

**Response:**
```json
{
    "status": "ok"
}
```
