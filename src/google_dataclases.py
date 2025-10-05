import json
from dataclasses import dataclass
from pprint import pprint
from typing import List, Dict, Any

# Define dataclasses from the most nested part outwards

@dataclass
class Option:
    value: str

@dataclass
class ChoiceQuestion:
    type: str
    options: List[Option]
    shuffle: bool

@dataclass
class Question:
    question_id: str
    required: bool
    choice_question: ChoiceQuestion

@dataclass
class QuestionItem:
    question: Question

@dataclass
class Item:
    item_id: str
    title: str
    question_item: QuestionItem

@dataclass
class Info:
    title: str
    document_title: str

@dataclass
class Settings:
    email_collection_type: str
    
@dataclass
class PublishState:
    is_published: bool
    is_accepting_responses: bool

@dataclass
class PublishSettings:
    publish_state: PublishState

# Main dataclass for the entire form
@dataclass
class GoogleForm:
    form_id: str
    info: Info
    settings: Settings
    revision_id: str
    responder_uri: str
    items: List[Item]
    publish_settings: PublishSettings
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GoogleForm':
        """
        Manually creates a GoogleForm instance from a dictionary.
        """
        # Create nested items by processing the dictionary data
        info_obj = Info(
            title=data["info"]["title"], 
            document_title=data["info"]["documentTitle"]
        )
        
        settings_obj = Settings(
            email_collection_type=data["settings"]["emailCollectionType"]
        )
        
        items_list = []
        for item_data in data["items"]:
            q_data = item_data["questionItem"]["question"]
            cq_data = q_data["choiceQuestion"]
            
            item_obj = Item(
                item_id=item_data["itemId"],
                title=item_data["title"],
                question_item=QuestionItem(
                    question=Question(
                        question_id=q_data["questionId"],
                        required=q_data["required"],
                        choice_question=ChoiceQuestion(
                            type=cq_data["type"],
                            options=[Option(value=opt["value"]) for opt in cq_data["options"]],
                            shuffle=cq_data["shuffle"]
                        )
                    )
                )
            )
            items_list.append(item_obj)
        
        publish_settings_obj = PublishSettings(
            publish_state=PublishState(
                is_published=data["publishSettings"]["publishState"]["isPublished"],
                is_accepting_responses=data["publishSettings"]["publishState"]["isAcceptingResponses"]
            )
        )
        
        # Instantiate the main class
        return cls(
            form_id=data["formId"],
            info=info_obj,
            settings=settings_obj,
            revision_id=data["revisionId"],
            responder_uri=data["responderUri"],
            items=items_list,
            publish_settings=publish_settings_obj
        )
