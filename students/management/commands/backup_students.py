import os
import datetime
import gnupg
from django.core.management.base import BaseCommand
from django.core import management


class Command(BaseCommand):
    help = 'Creates encrypted backups for specified apps with sensitive data protection'

    def handle(self, *args, **options):
        """
        Backup workflow:
        1. Create backup directory
        2. Generate timestamped backup file
        3. Export non-sensitive data
        4. Initialize GPG
        5. Encrypt backup
        6. Cleanup unencrypted data
        7. (On error) remove any partial files
        """

        backup_dir = 'encrypted_backups'
        recipient_email = 'admin@schoolhub.com'  
        excluded_models = [
            'students.HealthInformation',  # نموذج يحتوي على بيانات صحية حساسة
            'students.EconomicSituation'   # نموذج يحتوي على معلومات مالية حساسة
        ]

        try:
            # 2. إنشاء مجلد النسخ الاحتياطي إن لم يكن موجودًا
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

            # 3. تسمية الملفات المؤقتة والنهائية
            unencrypted_file = os.path.join(backup_dir, f"temp_{timestamp}.json")
            encrypted_file = os.path.join(backup_dir, f"backup_{timestamp}.gpg")

            # 4. استخراج البيانات (dumpdata) مع استثناء الـModels الحساسة
            with open(unencrypted_file, 'w', encoding='utf-8') as f:
                management.call_command(
                    'dumpdata',
                    'accounts',
                    'teachers',
                    'reports',
                    'students',
                    indent=2,
                    exclude=excluded_models,
                    stdout=f
                )

            gpg = gnupg.GPG(gnupghome=os.path.expanduser('~/.gnupg'))
            gpg.encoding = 'utf-8'

            with open(unencrypted_file, 'rb') as f:
                status = gpg.encrypt_file(
                    fileobj=f,
                    recipients=[recipient_email],
                    output=encrypted_file,
                    armor=False,
                    always_trust=True,
                    cipher_algo='AES256',
                    compress_algo='ZLIB'
                )

            if not status.ok:
                if os.path.exists(unencrypted_file):
                    os.remove(unencrypted_file)
                if os.path.exists(encrypted_file):
                    os.remove(encrypted_file)
                raise RuntimeError(f"Encryption failed: {status.status}")

            os.remove(unencrypted_file)

            self.stdout.write(
                self.style.SUCCESS(f'🔒 Encrypted backup created: {encrypted_file}')
            )

        except Exception as e:
            if os.path.exists(unencrypted_file):
                os.remove(unencrypted_file)
            if os.path.exists(encrypted_file):
                os.remove(encrypted_file)
            self.stdout.write(
                self.style.ERROR(f'❌ Backup failed: {str(e)}')
            )
