import sys

import pytest
from langchain.chat_models import ChatOpenAI
from loguru import logger

from sherpa_ai.agents import QAAgent
from sherpa_ai.connectors.chroma_vector_store import ChromaVectorStore
from sherpa_ai.events import EventType
from sherpa_ai.memory.shared_memory_with_vectordb import SharedMemoryWithVectorDB
from sherpa_ai.test_utils.llms import get_llm

data = """Avocados are a fruit, not a vegetable. They're technically considered a single-seeded berry, believe it or not.
The Eiffel Tower can be 15 cm taller during the summer, due to thermal expansion meaning the iron heats up, the particles gain kinetic energy and take up more space.
Trypophobia is the fear of closely-packed holes. Or more specifically, "an aversion to the sight of irregular patterns or clusters of small holes or bumps." No crumpets for them, then.
Allodoxaphobia is the fear of other people's opinions. It's a rare social phobia that's characterised by an irrational and overwhelming fear of what other people think.
Australia is wider than the moon. The moon sits at 3400km in diameter, while Australia’s diameter from east to west is almost 4000km.
'Mellifluous' is a sound that is pleasingly smooth and musical to hear.
The Spice Girls were originally a band called Touch. "When we first started [with the name Touch], we were pretty bland," Mel C told The Guardian in 2018. "We felt like we had to fit into a mould."
Emma Bunton auditioned for the role of Bianca Butcher in Eastenders. Baby Spice already had a small part in the soap back in the 90s but tried out for a full-time role. She was pipped to the post by Patsy Palmer but ended up auditioning for the Spice Girls not long after.
Human teeth are the only part of the body that cannot heal themselves. Teeth are coated in enamel which is not a living tissue.
It's illegal to own just one guinea pig in Switzerland. It's considered animal abuse because they're social beings and get lonely.
The Ancient Romans used to drop a piece of toast into their wine for good health - hence why we 'raise a toast'.
The heart of a shrimp is located in its head. They also have an open circulatory system, which means they have no arteries and their organs float directly in blood.
Amy Poehler was only seven years older than Rachel McAdams when she took on the role of "cool mom" in Mean Girls. Rachel was 25 as Regina George - Amy was 32 as her mum.
People are more creative in the shower. When we take a warm shower, we experience an increased dopamine flow that makes us more creative.
Baby rabbits are called kits. Cute!
my dog died on march 2021.
The unicorn is the national animal of Scotland. It was apparently chosen because of its connection with dominance and chivalry as well as purity and innocence in Celtic mythology.
The first aeroplane flew on December 17,1903 and  . Wilbur and Orville Wright made four brief flights at Kitty Hawk, North Carolina, with their first powered aircraft, aka the first airplane.
Venus is the only planet to spin clockwise. It travels around the sun once every 225 Earth days but it rotates clockwise once every 243 days.
Nutmeg is a hallucinogen. The spice contains myristicin, a natural compound that has mind-altering effects if ingested in large doses.
A 73-year-old bottle of French Burgundy became the most expensive bottle of wine ever sold at auction in 2018, going for $558,000 (approx £439,300). The bottle of 1945 Romanee-Conti sold at Sotheby for more than 17 times its original estimate of $32,000."""
session_id = "6"
meta_data = {
    "session_id": f"{session_id}",
    "file_name": "rtgfqq",
    "file_type": "pdf",
    "title": "NoMeaning",
    "data_type": "user_input",
}


@pytest.fixture
def config_logger():
    logger.remove()
    logger.add(sys.stderr, level="DEBUG")


@pytest.mark.external_api
def test_shared_memory_with_vector(config_logger, get_llm):
    llm = ChatOpenAI(model_name="gpt-3.5-turbo")
    # llm = get_llm(__file__, test_shared_memory_with_vector.__name__)
    # store text as a scraped text from a file with meta_data session_id
    split_data = ChromaVectorStore.file_text_splitter(data=data, meta_data=meta_data)
    ChromaVectorStore.chroma_from_texts(
        texts=split_data["texts"], meta_datas=split_data["meta_datas"]
    )

    shared_memory = SharedMemoryWithVectorDB(
        objective="summerize the file rtgfqq", agent_pool=None, session_id=session_id
    )

    task_agent = QAAgent(
        llm=llm,
        shared_memory=shared_memory,
    )

    shared_memory.add(
        EventType.task,
        "Planner",
        "summerize the file rtgfqq",
    )

    task_agent.run()

    results = shared_memory.get_by_type(EventType.result)

    assert len(results) == 1
    logger.debug(results[0].content)
