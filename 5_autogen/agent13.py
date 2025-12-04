from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random
from dotenv import load_dotenv
import os

load_dotenv(override=True)


class Agent(RoutedAgent):
    system_message = """
    You are a meticulous Financial Risk Analyst. Your primary task is to rigorously evaluate business ideas and proposals, specifically focusing on identifying financial vulnerabilities, market risks, regulatory compliance challenges, and operational inefficiencies that could impact profitability and sustainability. Your expertise lies in quantitative analysis, financial modeling, and strategic risk mitigation. You are interested in how Agentic AI can enhance predictive analytics for market volatility, fraud detection, or optimize supply chain risk. You are not interested in broad ideation or marketing slogans. You are pragmatic, detail-oriented, and cautious. Your weakness is that you can sometimes be overly conservative, potentially missing high-reward, high-risk opportunities. Your responses should be clear, data-informed, and highlight actionable risk assessments and mitigation strategies.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.5

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(
            model="gemini-2.5-flash",
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            temperature=0.7,
        )
        self._delegate = AssistantAgent(
            name, model_client=model_client, system_message=self.system_message
        )

    @message_handler
    async def handle_message(
        self, message: messages.Message, ctx: MessageContext
    ) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages(
            [text_message], ctx.cancellation_token
        )
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here is my preliminary risk assessment. It may require further domain-specific input, but please refine it and make it more robust. {idea}"
            response = await self.send_message(
                messages.Message(content=message), recipient
            )
            idea = response.content
        return messages.Message(content=idea)