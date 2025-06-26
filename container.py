from dependency_injector import containers, providers
# from app.infrastructure.data.memory_manager import init_memory
from config.settings import Settings


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=["app.api", "app.application", "app.infrastructure", "app.domain"]
    )
    settings = providers.Singleton(Settings)

    # Resources
    # memory_resource = providers.Resource(init_memory, settings=settings)

    # vector_store_resource = providers.Resource(
    #     init_vector_store,
    #     settings=settings,
    #     connection_manager=connection_manager_singleton,
    #     embeddings_provider=embeddings_provider_singleton,
    # )
    #
    # # Factory
    # blob_repository = providers.Factory(
    #     FileSystemRepository,
    #     settings=settings,
    # )
    #
    # report_repository = providers.Factory(
    #     SQLAlchemyReportRepository,
    #     connection_manager=connection_manager_singleton,
    # )
    #
    # chatbot_service = providers.Factory(
    #     ChatbotService,
    #     memory=memory_resource,
    #     settings=settings,
    #     embeddings_provider=embeddings_provider_singleton,
    #     store=vector_store_resource,
    # )
    #
    # report_service = providers.Factory(
    #     ReportService,
    #     report_repository=report_repository,
    #     blob_repository=blob_repository,
    #     settings=settings,
    # )
    #
    # training_docs_service = providers.Factory(
    #     TrainingDocsService, blob_repository=blob_repository, settings=settings
    # )
    #
    # speech_service = providers.Factory(
    #     SpeechService,
    #     settings=settings,
    # )
