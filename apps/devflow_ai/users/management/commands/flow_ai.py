from django.core.management import call_command
from django.core.management.base import BaseCommand,CommandError

from django.db import connections

class Command(BaseCommand):
    help = "Run flow database migrations safely"

    def add_arguments(self, parser):
        parser.add_argument("--no-makemigrations",action="store_true")
        parser.add_argument("--no-migrate",action="store_true")
        parser.add_argument("--no-input",action="store_true")
        parser.add_argument("--database",default=None)

    def handle(self, *args, **options):
        run_makemigrations = options["no_makemigrations"]
        skip_migrate = options["no_migrate"]
        no_input = options["no_input"]
        database = options["database"]

        if database and database not in connections.databases:
            raise CommandError(
                f"알수 없는 database alias입니다:'{database}'."
                f"사용 가능 alias:{','.join(connections.databases.keys())}"
            )
        command_kwargs = {
            "interactive" : not no_input,
            "verbosity": options.get("verbosity",1)
        }
        migrate_kwargs = dict(command_kwargs)
        if database:
            migrate_kwargs["database"] = database
        self.stdout.write(self.style.NOTICE("🚀Starting flow migrations..." ))

        made_migrations = False
        if run_makemigrations:
            self.stdout.write(self.style.WARNING("📦Running makemigrations..."))
            try:
                call_command("makemigrations",**command_kwargs)
                made_migrations = True
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"[makemigrations 단계실패]{e}"))
                raise CommandError(
                    "flow failed at makemigrations step"
                )from e
        if not skip_migrate:
            self.stdout.write(self.style.WARNING("🗄️Running migrate..."))
            try:
                call_command("migrate",**migrate_kwargs)
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"[migrate 단계실패]{e}"))
                if made_migrations:
                    self.stderr.write(self.style.WARNING(
                        "⚠️  makemigrations로 생성된 migration 파일이 "
                        "디스크에 그대로 남아 있을 수 있습니다. "
                        "DB는 반영되지 않았으니 migration 파일을 확인 후 "
                        "필요하면 수동으로 삭제/조정하세요."
                    ))
                    raise CommandError(
                        "flow failed at migrate step"
                    )from e
        self.stdout.write(self.style.SUCCESS("✅flow_ai complete"))