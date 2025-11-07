from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Max


class Command(BaseCommand):
    help = "Print the highest PK value for a given model"

    def add_arguments(self, parser):
        parser.add_argument(
            "model_args",
            nargs="+",
            help=(
                'Model to inspect: either "app_label.ModelName" '
                "or two args: app_label model_name"
            ),
        )

    def handle(self, *args, **options):
        model_args = options["model_args"]

        # parse either "app_label.ModelName" or ["app_label", "ModelName"]
        if len(model_args) == 1 and "." in model_args[0]:
            try:
                app_label, model_name = model_args[0].split(".", 1)
            except ValueError:
                raise CommandError(
                    "When using a single argument, it must be 'app_label.ModelName'"
                )
        elif len(model_args) == 2:
            app_label, model_name = model_args
        else:
            raise CommandError(
                "Provide either one arg 'app_label.ModelName' or two args: app_label model_name"  # noqa: E501
            )

        model = apps.get_model(app_label, model_name)
        if model is None:
            raise CommandError(f"No model found for {app_label}.{model_name}")

        # aggregate on the PK field (works even if you've got a custom PK name)
        result = model.objects.aggregate(max_pk=Max(model._meta.pk.name))
        max_pk = result["max_pk"]

        self.stdout.write(f"Max PK for {app_label}.{model_name} → {max_pk!r}")
