import llm
from typing import Dict
from prompts.support_genie import PROMPT as SUPPORT_GENIE_PROMPT

class HelpService:
    @classmethod
    def extract_citations(cls, *, citations: list) -> list:
        urls = set()
        for citation in citations:
            for reference in citation["retrievedReferences"]:
                urls.add(reference['location']['webLocation']['url'])
        return list(urls)

    @classmethod
    def format_response(cls, *, response: Dict) -> str:
        # Extract citations
        citations = cls.extract_citations(citations=response["citations"])

        # Format response
        formatted_response = response["output"]["text"]
        if citations:
            formatted_response = formatted_response + "\n\n*Sources:*\n" + "\n".join(citations)

        return formatted_response

    @classmethod
    def get_support_response(cls, *, user_query: str) -> str:
        response = llm.get_support_response_from_bedrock(
            prompt_template=SUPPORT_GENIE_PROMPT,
            input_message=user_query
        )

        return cls.format_response(response=response)
