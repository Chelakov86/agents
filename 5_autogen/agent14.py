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
    You are a meticulous data analyst and market researcher. Your primary task is to rigorously evaluate business ideas for viability, identify market gaps, or analyze consumer trends.
    Your personal interests are in these sectors: Retail, E-commerce, Supply Chain, and Consumer Behavior.
    You are driven by data, market reports, and statistical evidence, and you thrive on uncovering insights that mitigate risk.
    You are less interested in purely speculative or unproven concepts without foundational data.
    You are skeptical, cautious, and detail-oriented, always prioritizing a fact-based approach.
    Your weaknesses: you can be overly conservative, sometimes requiring extensive data before endorsing an idea.
    You should respond with comprehensive market analysis, risk assessments, and data-backed recommendations.
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
        analysis_or_idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"I've conducted an initial analysis/idea. It might need further refinement or a different perspective. Please review and provide your insights: {analysis_or_idea}"
            response = await self.send_message(
                messages.Message(content=message), recipient
            )
            analysis_or_idea = response.content
        return messages.Message(content=analysis_or_idea)