"""
LLM Service for AI generation
"""
from typing import Optional, Dict, List
import google.generativeai as genai
from loguru import logger

from app.core.config import settings

# Optional: OpenAI support (commented out by default)
# Uncomment if you want to use OpenAI
# from openai import OpenAI


class LLMService:
    """Unified LLM service supporting multiple providers"""
    
    def __init__(self):
        """Initialize LLM clients"""
        self.default_provider = settings.DEFAULT_LLM
        
        # Initialize Google Gemini (REQUIRED)
        if settings.GOOGLE_API_KEY:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
            logger.info("Initialized Google Gemini")
        else:
            raise ValueError("GOOGLE_API_KEY is required in .env file")
        
        # Initialize OpenAI (OPTIONAL)
        # Uncomment if you have OPENAI_API_KEY configured
        # if settings.OPENAI_API_KEY:
        #     self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        #     logger.info("Initialized OpenAI")
        # else:
        #     self.openai_client = None
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        provider: Optional[str] = None
    ) -> str:
        """
        Generate text using LLM
        
        Args:
            prompt: User prompt
            system_prompt: System instruction
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            provider: LLM provider (gemini, openai, or None for default)
            
        Returns:
            Generated text
        """
        try:
            provider = provider or self.default_provider
            
            if 'gemini' in provider.lower():
                return self._generate_gemini(prompt, system_prompt, temperature, max_tokens)
            elif 'gpt' in provider.lower() or 'openai' in provider.lower():
                return self._generate_openai(prompt, system_prompt, temperature, max_tokens)
            else:
                return self._generate_gemini(prompt, system_prompt, temperature, max_tokens)
                
        except Exception as e:
            logger.error(f"Error generating with LLM: {e}")
            raise
    
    def _generate_gemini(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> str:
        """Generate using Google Gemini"""
        try:
            # Combine system prompt with user prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            else:
                full_prompt = prompt
            
            # Generate response
            response = self.gemini_model.generate_content(
                full_prompt,
                generation_config=genai.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error with Gemini: {e}")
            raise
    
    def _generate_openai(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> str:
        """Generate using OpenAI (OPTIONAL - requires openai package and API key)"""
        # Uncomment if you want to use OpenAI
        raise NotImplementedError("OpenAI support is disabled. Enable it in llm_service.py if needed.")
        
        # Uncomment below and install openai package to enable:
        # try:
        #     if not hasattr(self, 'openai_client') or self.openai_client is None:
        #         raise ValueError("OpenAI client not initialized. Add OPENAI_API_KEY to .env")
        #     
        #     messages = []
        #     if system_prompt:
        #         messages.append({"role": "system", "content": system_prompt})
        #     messages.append({"role": "user", "content": prompt})
        #     
        #     response = self.openai_client.chat.completions.create(
        #         model="gpt-4-turbo-preview",
        #         messages=messages,
        #         temperature=temperature,
        #         max_tokens=max_tokens
        #     )
        #     return response.choices[0].message.content
        # except Exception as e:
        #     logger.error(f"Error with OpenAI: {e}")
        #     raise
    
    def generate_with_context(
        self,
        query: str,
        context: str,
        chat_history: Optional[List[Dict]] = None,
        temperature: float = 0.7
    ) -> str:
        """
        Generate response with RAG context
        
        Args:
            query: User query
            context: Retrieved context
            chat_history: Previous chat messages
            temperature: Sampling temperature
            
        Returns:
            Generated response
        """
        try:
            # Build system prompt
            system_prompt = """You are an AI study assistant helping students prepare for exams. 
Your role is to answer questions based on the provided study materials.

Guidelines:
- Answer questions accurately based on the provided context
- If the context doesn't contain the answer, say so clearly
- Provide examples and explanations when helpful
- Be concise but thorough
- Reference specific concepts from the materials when relevant"""
            
            # Build user prompt with context
            user_prompt = f"""Context from study materials:
{context}

Question: {query}

Please provide a detailed answer based on the context above."""
            
            # Add chat history if available
            if chat_history:
                history_text = "\n".join([
                    f"{msg['role']}: {msg['content']}" 
                    for msg in chat_history[-3:]  # Last 3 messages
                ])
                user_prompt = f"Previous conversation:\n{history_text}\n\n{user_prompt}"
            
            return self.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=temperature
            )
            
        except Exception as e:
            logger.error(f"Error generating with context: {e}")
            raise
    
    def stream_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ):
        """
        Generate text with streaming (for real-time responses)
        
        Args:
            prompt: User prompt
            system_prompt: System instruction
            temperature: Sampling temperature
            
        Yields:
            Text chunks
        """
        try:
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            else:
                full_prompt = prompt
            
            # Use Gemini for streaming
            response = self.gemini_model.generate_content(
                full_prompt,
                generation_config=genai.GenerationConfig(temperature=temperature),
                stream=True
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            logger.error(f"Error streaming: {e}")
            raise


# Global LLM service instance
llm_service = LLMService()
