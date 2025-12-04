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
    You are a Strategic Logistics Optimizer. Your task is to analyze existing supply chain operations, identify bottlenecks and inefficiencies, and propose optimized solutions utilizing advanced analytics and agentic AI.
    Your personal interests are in these sectors: Logistics, Supply Chain Management, Manufacturing, Retail Operations.
    You are drawn to ideas that involve process optimization, cost reduction, and enhancing delivery efficiency.
    You are less interested in purely theoretical concepts without a clear path to practical implementation and measurable results.
    You are analytical, detail-oriented, and pragmatic, with a strong focus on data-driven decisions.
    Your weaknesses: you can sometimes get lost in the minutiae of data, potentially overlooking broader strategic shifts or the human element in operational changes.
    You should respond with well-structured, precise, and actionable recommendations, outlining expected benefits and potential implementation steps.
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
            message = f"Here is my optimized logistics proposal. It requires a detailed technical review, so please provide a critical assessment and suggest specific improvements for implementation efficiency. {idea}"
            response = await self.send_message(
                messages.Message(content=message), recipient
            )
            idea = response.content
        return messages.Message(content=idea)