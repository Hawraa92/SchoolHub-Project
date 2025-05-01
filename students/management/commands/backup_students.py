import os
import datetime
import gnupg
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Creates encrypted backups for specified apps with sensitive data protection using symmetric encryption'

    def handle(self, *args, **options):
        backup_dir = 'encrypted_backups'
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

        # تعديل اسم المستخدم واسم قاعدة البيانات حسب إعداداتك
        unencrypted_file = os.path.join(backup_dir, f"temp_{timestamp}.sql")
        encrypted_file = os.path.join(backup_dir, f"backup_{timestamp}.gpg")

        dump_command = f"pg_dump -U your_username your_dbname > {unencrypted_file}"
        result = os.system(dump_command)
        if result != 0:
            self.stdout.write(self.style.ERROR("pg_dump command failed"))
            return

        # تهيئة GPG للتشفير المتماثل
        gpg = gnupg.GPG(gnupghome=os.path.expanduser('~/.gnupg'))
        gpg.encoding = 'utf-8'

        with open(unencrypted_file, 'rb') as f:
            status = gpg.encrypt_file(
                fileobj=f,
                symmetric='AES256',  # استخدام التشفير المتماثل مع AES256
                output=encrypted_file,
                armor=False,
                always_trust=True,
                compress_algo='ZLIB'
            )

        if not status.ok:
            if os.path.exists(unencrypted_file):
                os.remove(unencrypted_file)
            if os.path.exists(encrypted_file):
                os.remove(encrypted_file)
            raise RuntimeError(f"Encryption failed: {status.status}")

        os.remove(unencrypted_file)
        self.stdout.write(self.style.SUCCESS(f"🔒 Encrypted backup created: {encrypted_file}"))
