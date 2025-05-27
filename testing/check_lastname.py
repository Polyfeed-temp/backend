#!/usr/bin/env python3
import os
os.environ['USER_ENCRYPTION_KEY'] = 'dkdpYkkzRU9QMnJIaG9xMHltNWZMTTUtWXRtbUxpc0J4aEIwcWRjS3ROcz0='

from src.database import get_db
from src.user.encryption import get_encryption
from sqlalchemy import text

db = next(get_db())
encryption = get_encryption()

result = db.execute(text('SELECT lastName FROM USER WHERE lastName IS NOT NULL LIMIT 10')).fetchall()
print('lastName values:')
for i, row in enumerate(result):
    value = row[0]
    is_encrypted = encryption.is_encrypted(value) if value else False
    print(f'{i+1}. {value} (encrypted: {is_encrypted})') 