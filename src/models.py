from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Speaker:
    """Модель данных спикера"""
    speaker_url: str = ""
    speaker_slug: str = ""
    name: str = ""
    position: str = ""
    company: str = ""
    country: str = ""
    description: str = ""
    social_network: str = ""
    session_date: str = ""
    session_time: str = ""
    session_location: str = ""
    session_topic_link: str = ""
    session_topic_title: str = ""

    def to_dict(self) -> dict:
        """Преобразует объект в словарь"""
        return {
            'speaker_url': self.speaker_url,
            'speaker_slug': self.speaker_slug,
            'name': self.name,
            'position': self.position,
            'company': self.company,
            'country': self.country,
            'description': self.description,
            'social_network': self.social_network,
            'session_date': self.session_date,
            'session_time': self.session_time,
            'session_location': self.session_location,
            'session_topic_link': self.session_topic_link,
            'session_topic_title': self.session_topic_title
        }


@dataclass
class SpeakerSlug:
    """Модель для хранения slug спикера"""
    slug: str
    name: str = ""
