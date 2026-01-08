"""
LLM service for generating responses using OpenAI.
"""
from openai import OpenAI
from app.config import get_settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class LLMService:
    """Service for interacting with OpenAI LLM."""
    
    def __init__(self):
        """Initialize LLM service with OpenAI client."""
        self.settings = get_settings()
        self.client = OpenAI(api_key=self.settings.openai_api_key)
        self.model = self.settings.openai_model
        logger.info(f"LLM Service initialized with model: {self.model}")
    
    def generate_response(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Generate response from LLM.
        
        Args:
            prompt: The prompt to send to the LLM
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
        
        Returns:
            Generated text response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的课程顾问助手。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            answer = response.choices[0].message.content
            logger.info(f"Generated response with {len(answer)} characters")
            return answer
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "抱歉，我现在无法回答您的问题。请稍后再试。"
    
    def generate_with_context(
        self,
        question: str,
        context: str,
        prompt_template: str
    ) -> str:
        """
        Generate response with context using a prompt template.
        
        Args:
            question: User's question
            context: Retrieved context from documents
            prompt_template: Prompt template with {context} and {question} placeholders
        
        Returns:
            Generated answer
        """
        prompt = prompt_template.format(context=context, question=question)
        return self.generate_response(prompt)
