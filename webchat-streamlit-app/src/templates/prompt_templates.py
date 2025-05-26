"""
Prompt templates for different AI providers and use cases
"""
from langchain.prompts import PromptTemplate


def get_qa_chain_prompt(website_name: str = "BotPenguin") -> PromptTemplate:
    """
    Get QA chain prompt template with customizable website name
    
    Args:
        website_name: Name of the website/brand for chatbot persona
        
    Returns:
        PromptTemplate: Configured prompt template
    """
    template = f"""Use the following pieces of context to answer the question at the end. 
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Answer the question as you are a helpful chatbot assistant for {website_name}. 
Keep the answer as concise as possible while being informative.
Always say "thanks for asking!" at the end of the answer.

Context:
{{context}}

Question: {{question}}

Helpful Answer:"""
    
    return PromptTemplate.from_template(template)


def get_openai_system_prompt(website_name: str = "BotPenguin") -> str:
    """Get system prompt specifically optimized for OpenAI models"""
    return f"""You are a helpful AI assistant representing {website_name}. 
Your role is to provide accurate, helpful, and concise answers based on the provided context.
Always be polite, professional, and end your responses with "thanks for asking!"
If you don't know something, admit it rather than making up information."""


def get_gemini_system_prompt(website_name: str = "BotPenguin") -> str:
    """Get system prompt specifically optimized for Gemini models"""
    return f"""You are an intelligent AI assistant for {website_name}. 
Use the provided context to answer questions accurately and helpfully.
Be concise but informative in your responses.
Always maintain a friendly, professional tone and end with "thanks for asking!"
If the answer isn't in the context, politely say you don't know."""


def get_chat_prompt_template(provider: str, website_name: str = "BotPenguin") -> PromptTemplate:
    """
    Get chat prompt template optimized for specific AI provider
    
    Args:
        provider: AI provider ('openai' or 'gemini')
        website_name: Name of the website/brand
        
    Returns:
        PromptTemplate: Provider-optimized prompt template
    """
    if provider == "openai":
        system_prompt = get_openai_system_prompt(website_name)
    elif provider == "gemini":
        system_prompt = get_gemini_system_prompt(website_name)
    else:
        system_prompt = get_openai_system_prompt(website_name)  # Default fallback
    
    template = f"""{system_prompt}

Context from website:
{{context}}

User Question: {{question}}

Assistant Response:"""
    
    return PromptTemplate.from_template(template)