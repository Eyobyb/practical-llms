from sherpa_ai.connectors.chroma_vector_store import ChromaVectorStore
from sherpa_ai.memory import SharedMemory
from typing import List, Optional

from langchain.embeddings.openai import OpenAIEmbeddings

from sherpa_ai.actions.planning import Plan
from sherpa_ai.agents import AgentPool
from sherpa_ai.events import Event, EventType
from sherpa_ai.memory.belief import Belief



class SharedMemoryWithVectorDB(SharedMemory):
    """
    Custom implementation of SharedMemory that integrates with ChromaVectorStore.

    Use this class whenever context retrieval from a vector database is needed.

    Attributes:
        session_id (str): Unique identifier for the current session.
                                                                                          
    """

    def __init__(
        self,
        objective: str,
        session_id: str,
        agent_pool: AgentPool = None,
    ):
        self.objective = objective
        self.agent_pool = agent_pool
        self.events: List[Event] = []
        self.plan: Optional[Plan] = None
        self.current_step = None
        self.session_id = session_id

    def observe(self, belief: Belief):
        vec_db = ChromaVectorStore.chroma_from_existing()

        tasks = super().get_by_type(EventType.task)

        task = tasks[-1] if len(tasks) > 0 else None

        # based on the current task search similarity on the context and add it as an 
        # event type user_input which is going to be used as a context on the prompt
        contexts = vec_db.similarity_search(task.content, session_id=self.session_id)

        # Loop through the similarity search results, add the chunks as user_input events which will be added as a context in the belief class.
        for context in contexts:
            super().add(
                agent="",
                event_type=EventType.user_input,
                content=context.page_content,
            )


        belief.set_current_task(task)


        for event in self.events:
            if event.event_type in [EventType.task, EventType.result, EventType.user_input]:
                belief.update(event)
