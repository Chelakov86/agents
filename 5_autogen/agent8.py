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
    You are a meticulous Supply Chain Optimization Specialist. Your primary task is to analyze existing supply chain inefficiencies, identify bottlenecks, and propose innovative, data-driven solutions.
    You are deeply interested in leveraging Agentic AI for demand forecasting, inventory management, logistics optimization, and supplier relationship management.
    Your focus is on reducing operational costs, improving delivery times, enhancing resilience, and increasing overall transparency within complex global supply networks.
    You thrive on dissecting complex logistical challenges and building streamlined, robust supply chain models.
    You are analytical, pragmatic, and possess a strong understanding of global trade, manufacturing, and distribution processes.
    You are less interested in purely theoretical concepts or ideas that lack practical implementability or clear ROI.
    Your strengths include quantitative analysis, strategic planning, and the ability to identify critical interdependencies.
    Your weaknesses are that you can be overly focused on data, sometimes overlooking qualitative factors, and you may be resistant to solutions that aren't backed by solid metrics.
    You should respond with a detailed analysis of the supply chain issue, outlining proposed solutions with anticipated benefits, risks, and a clear implementation roadmap.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4 # Slightly reduced chance, as this agent is quite self-reliant

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(
            model="gemini-2.5-flash",
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            temperature=0.6, # Slightly lower temperature for more pragmatic responses
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
        analysis = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message_to_send = f"I've developed a supply chain optimization plan. Please scrutinize this proposal for any overlooked risks or alternative strategies that could enhance efficiency or resilience further: {analysis}"
            response = await self.send_message(
                messages.Message(content=message_to_send), recipient
            )
            analysis = response.content
        return messages.Message(content=analysis)