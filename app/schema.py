from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


class TopicInput(BaseModel):
    text: str = Field(
        ...,
        description="Input text for topic classification",
        example="Keterlibatan SEC dalam penyelidikan terhadap Exxon menunjukkan komitmen mereka untuk memastikan transparansi mengenai risiko iklim yang dihadapi perusahaan dan investor mereka.",
    )


class TopicResult(BaseModel):
    topic: Dict[str, float] = Field(
        ..., description="Dictionary of topic predictions with confidence scores"
    )
    subtopic: Dict[str, float] = Field(
        ..., description="Dictionary of subtopic predictions with confidence scores"
    )


class TopicOutput(BaseModel):
    result: TopicResult = Field(..., description="Result of the topic analysis")

    class Config:
        json_schema_extra = {
            "example": {
                "result": {
                    "topic": {"konservasi lingkungan": 0.8862940073013306},
                    "subtopic": {"peran pemerintah lokal": 0.7940667867660522},
                }
            }
        }


class CheckInput(BaseModel):
    text: str = Field(
        ...,
        description="Input text for veracity check",
        example="Penyelidikan oleh jaksa penuntut di New York, Maryland, California, dan Kepulauan Virgin yang memeriksa apakah tindakan ExxonMobil melanggar undang-undang perlindungan konsumen atau investor menunjukkan pentingnya memastikan bahwa perusahaan bahan bakar fosil mematuhi peraturan terkait perubahan iklim.",
    )


class NewsItem(BaseModel):
    title: str
    content: str
    url: str
    score: float
    stance: str
    hoax_status: str


class Knowledges(BaseModel):
    class Knowledge(BaseModel):
        collection_name: str
        documents_count: int

    result: List[Knowledge]


class Article(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    content: Optional[str] = None
    html_content: Optional[str] = None
    short_content: Optional[str] = None
    created_by: Optional[str] = None
    localtime: Optional[str] = None
    publish_localtime: Optional[str] = None
    user_publish_date: Optional[str] = None
    stamped_image_url: Optional[List[str]] = None
    classification: Optional[str] = None
    category: Optional[str] = None
    status_name: Optional[str] = None
    status_reason: Optional[str] = None
    status_created_by: Optional[str] = None
    status_localtime: Optional[str] = None
    tags: Optional[List[str]] = None
    verify_url: Optional[List[str]] = None
    distributions: Optional[List[str]] = None
    source_description: Optional[str] = None
    stance: Optional[str] = ""
    hoax_status: Optional[str] = ""
    score: Optional[float] = 0
    jaccard_score: Optional[float] = 0
    url: Optional[str] = ""

    class Config:
        json_schema_extra = {
            "example": {
                "id": 19206,
                "title": "Akun Instagram Mengatasnamakan Rumah Sakit Hermina",
                "content": "Beredar sebuah informasi bahwa lantai tiga Rumah Sakit..",
                "html_content": "Beredar sebuah informasi bahwa lantai tiga Rumah Sakit..",
                "short_content": "Beredar sebuah informasi bahwa lantai tiga Rumah Sakit..",
                "created_by": "Dedy",
                "localtime": "2022-12-21 07:50:56",
                "publish_localtime": None,
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
                "tags": ["gempa", "karangasem"],
                "verify_url": [],
                "distributions": [],
                "source_description": "https://www.youtube.com/shorts/2c_zICAym7U",
                "stance": "support",
                "hoax_status": "hoax",
                "score": 0,
                "jaccard_score": 0,
                "url": "",
            }
        }


class CheckOutput(BaseModel):
    relevant_items: List[Union[NewsItem, Article]]
    hoax_probability: float

    @validator("hoax_probability")
    def validate_probability(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("Probability must be between 0 and 1")
        return v


class InsertOutput(BaseModel):
    status: str = Field(
        ...,
        description="status explanation for insert item",
        example="item id 19206 is inserted into climate_hoax",
    )


class DeleteOutput(BaseModel):
    status: str = Field(
        ...,
        description="status explanation for deleted item",
        example="item id 19206 is deleted from [climate_hoax, climate_fact]",
    )
