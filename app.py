import datetime
import os
import shutil

from dotenv import load_dotenv

# Load environment variables BEFORE importing services.

load_dotenv()

from config.settings import CHROMA_DB_PATH, MAX_CONVERSATION_MESSAGES
from models.collection import Collection
from services.conversation import ConversationService
from services.conversation_memory import ConversationMemory
from services.crew_service import run_autonomous_research
from services.index_manager import IndexManager
from services.pipeline import initialize_pipeline


def _select_collection(
    index_manager: IndexManager,
) -> Collection:
    """
    Prompt the user to select a document collection.
    """

    collections = index_manager.list_collections()

    if not collections:
        raise RuntimeError("No document collections found.")

    print("\n📚 Available collections:\n")

    for selection_index, collection in enumerate(
        collections,
        start=1,
    ):
        print(
            f"{selection_index}. "
            f"{collection.name} "
            f"({collection.document_count} documents)"
        )

    collection_lookup = {
        collection.name.lower(): collection for collection in collections
    }

    while True:

        selection = input("\nSelect a collection: ").strip()

        if selection.isdigit():

            selection_index = int(selection)

            if 1 <= selection_index <= len(collections):
                return collections[selection_index - 1]

        else:

            collection = collection_lookup.get(selection.lower())

            if collection is not None:
                return collection

        print("Invalid collection. Please try again.")


def main() -> None:
    """
    Start the research assistant.
    """

    index_manager = initialize_pipeline()

    try:
        collection = _select_collection(
            index_manager,
        )

    except RuntimeError as error:
        print(f"❌ {error}")
        return

    vector_store = index_manager.get_vector_store(
        collection.name,
    )

    memory = ConversationMemory(
        max_messages=MAX_CONVERSATION_MESSAGES,
    )

    conversation = ConversationService(
        vector_store=vector_store,
        memory=memory,
    )

    while True:
        print("\n🤖 Intelligent Agentic Research Assistant")
        print(f"📚 Active Collection: {collection.name}")
        print("-" * 42)
        print("1. Start Interactive Q&A Chat Session")
        print("2. Start Autonomous Research & Report Generation (v3.0.0)")
        print("3. View Past Research Reports Logs (LTM)")
        print("4. Update Research Style Preferences (LTM)")
        print("5. Change Document Collection")
        print("6. Rebuild Current Collection Index")
        print("7. Clear Conversational Memory")
        print("8. Exit")
        print("-" * 42)

        choice = input("Select an option (1-8): ").strip()

        if choice == "1":
            print(
                "\n💬 Entering Q&A Chat Session (type 'exit' to return to menu, 'clear' to clear memory)"
            )
            while True:
                question = input("\nYou: ").strip()
                if not question:
                    continue

                if question.lower() == "exit":
                    break
                elif question.lower() == "clear":
                    conversation.clear()
                    print("\n🧹 Conversation memory cleared.")
                    continue

                response = conversation.ask(question)

                if response is None:
                    print(
                        "\nI need more context to understand "
                        "your question. Please clarify what "
                        "you are referring to."
                    )
                    continue

                print(f"\n{response.answer}")
                print(f"\nSource: {response.source.value}")
                print(f"Confidence: {response.confidence.value}")

                if response.citations:
                    print("\nReferences:")
                    for citation in response.citations:
                        print(f"- {citation.title}")
                        print(f"  {citation.location}")
                        if citation.url:
                            print(f"  {citation.url}")

        elif choice == "2":
            topic = input(
                "\nEnter research topic (e.g., 'Compare BERT and Transformer architectures'): "
            ).strip()
            if not topic:
                print("Topic cannot be empty.")
                continue

            print(f"\n🚀 Launching autonomous research crew for topic: '{topic}'...")
            print(
                "Running Planning, Gathering, and Synthesis steps (verbose logs outputted below)...\n"
            )

            try:
                report = run_autonomous_research(topic, vector_store)

                # Save report to outputs/
                os.makedirs("outputs", exist_ok=True)
                timestamp = datetime.datetime.now(datetime.timezone.utc).strftime(
                    "%Y%m%d_%H%M%S"
                )
                filename = f"outputs/research_report_{timestamp}.md"

                with open(filename, "w", encoding="utf-8") as f:
                    f.write(report)

                print("\n==========================================")
                print("✅ Autonomous Research Completed Successfully!")
                print(f"📄 Report Saved To: {filename}")
                print("==========================================")
            except Exception as e:  # noqa: BLE001
                print(f"\n❌ Research failed: {e}")

        elif choice == "3":
            from services.memory_service import list_past_topics

            past_topics = list_past_topics()
            if not past_topics:
                print("\n📂 No past research reports logged in LTM database.")
                continue

            print("\n📋 Past Research Logs:")
            for index, (past_topic, timestamp) in enumerate(past_topics, start=1):
                print(f"{index}. [{timestamp}] {past_topic}")

            select_val = input(
                "\nEnter log number to display full report (or press Enter to return): "
            ).strip()
            if select_val.isdigit():
                sel_idx = int(select_val)
                if 1 <= sel_idx <= len(past_topics):
                    target_topic = past_topics[sel_idx - 1][0]
                    # Print the database entry
                    conn_path = os.path.join(CHROMA_DB_PATH.parent, "memory.db")
                    import sqlite3

                    conn = sqlite3.connect(conn_path)
                    try:
                        cursor = conn.cursor()
                        cursor.execute(
                            "SELECT report FROM research_history WHERE topic = ?",
                            (target_topic,),
                        )
                        row = cursor.fetchone()
                        if row:
                            print("\n==========================================")
                            print(f"Report: {target_topic}")
                            print("==========================================\n")
                            print(row[0])
                            print("\n==========================================")
                    finally:
                        conn.close()
                else:
                    print("Invalid index.")

        elif choice == "4":
            from services.memory_service import get_preference, set_preference

            curr_depth = get_preference("research_depth", "comprehensive")
            curr_style = get_preference("report_style", "professional technical report")

            print("\n⚙️ Current Preferences:")
            print(f"- Depth: {curr_depth}")
            print(f"- Style: {curr_style}")

            print("\nSelect Research Depth:")
            print("1. comprehensive (detailed multi-stage searches)")
            print("2. quick overview (short target summaries)")
            depth_sel = input(
                "Select depth (1-2, press Enter to keep current): "
            ).strip()
            if depth_sel == "1":
                set_preference("research_depth", "comprehensive")
            elif depth_sel == "2":
                set_preference("research_depth", "quick overview")

            print("\nSelect Report Output Style:")
            print("1. professional technical report")
            print("2. concise executive summary")
            print("3. detailed step-by-step tutorial")
            style_sel = input(
                "Select style (1-3, press Enter to keep current): "
            ).strip()
            if style_sel == "1":
                set_preference("report_style", "professional technical report")
            elif style_sel == "2":
                set_preference("report_style", "concise executive summary")
            elif style_sel == "3":
                set_preference("report_style", "detailed step-by-step-tutorial")

            print("\n✅ Preferences updated in LTM database.")

        elif choice == "5":
            try:
                collection = _select_collection(index_manager)
                vector_store = index_manager.get_vector_store(collection.name)
                conversation = ConversationService(
                    vector_store=vector_store, memory=memory
                )
                print(f"\n🔄 Switched to Collection: {collection.name}")
            except RuntimeError as error:
                print(f"\n❌ {error}")

        elif choice == "6":
            print(f"\n🔨 Rebuilding index for collection '{collection.name}'...")
            try:
                # Force rebuild by deleting the local DB directory and clearing cache
                db_path = CHROMA_DB_PATH / collection.name
                if db_path.is_dir():
                    shutil.rmtree(db_path)
                if collection.name in index_manager._vector_stores:
                    del index_manager._vector_stores[collection.name]

                vector_store = index_manager.get_vector_store(collection.name)
                conversation = ConversationService(
                    vector_store=vector_store, memory=memory
                )
                print("✅ Index rebuilt successfully.")
            except Exception as e:  # noqa: BLE001
                print(f"❌ Failed to rebuild index: {e}")

        elif choice == "7":
            conversation.clear()
            print("\n🧹 Conversation memory cleared.")

        elif choice == "8":
            print("\n👋 Goodbye!")
            break
        else:
            print("\nInvalid choice. Please enter a number between 1 and 8.")


if __name__ == "__main__":
    main()
