import sqlite3
import hashlib
import random
import math
from pathlib import Path
from dataclasses import dataclass
from typing import Tuple, List

from sukiaTrueSkill import Rating, match1v1


@dataclass
class Image:
    hash: str
    path: str
    rating: Rating
    match_count: int


class RatingDB:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS images (
                hash TEXT PRIMARY KEY,
                path TEXT NOT NULL,
                mean REAL DEFAULT 25.0,
                var REAL DEFAULT 69.39,
                match_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # 触发器：更新时自动刷新 updated_at
        self.conn.execute('''
            CREATE TRIGGER IF NOT EXISTS update_timestamp
            AFTER UPDATE ON images
            BEGIN
                UPDATE images SET updated_at = CURRENT_TIMESTAMP WHERE hash = NEW.hash;
            END
        ''')
        self.conn.commit()

    @staticmethod
    def _hash_file(path: str) -> str:
        sha256 = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

    def init_from_folder(self, folder_path: str) -> dict:
        """
        扫描文件夹，返回 {'new': n, 'updated': m}
        """
        folder = Path(folder_path)
        extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
        stats = {'new': 0, 'updated': 0}

        for file_path in folder.rglob('*'):
            if file_path.suffix.lower() not in extensions:
                continue

            path_str = str(file_path.resolve())
            file_hash = self._hash_file(path_str)

            # 检查是否已存在
            existing = self.conn.execute(
                'SELECT path FROM images WHERE hash = ?', (file_hash,)
            ).fetchone()

            if existing is None:
                self.conn.execute(
                    'INSERT INTO images (hash, path) VALUES (?, ?)',
                    (file_hash, path_str)
                )
                stats['new'] += 1
            elif existing[0] != path_str:
                # 哈希相同但路径不同，更新路径
                self.conn.execute(
                    'UPDATE images SET path = ? WHERE hash = ?',
                    (path_str, file_hash)
                )
                stats['updated'] += 1

        self.conn.commit()
        return stats

    def sample_pair(self) -> Tuple[Image, Image]:
        """
        抽取一对：高 var 端一个，低 var 端一个
        """
        rows = self.conn.execute('''
            SELECT hash, path, mean, var, match_count 
            FROM images ORDER BY var DESC
        ''').fetchall()

        n = len(rows)
        if n < 2:
            raise ValueError(f"图片数量不足: {n}")

        # 半正态采样
        # 高 var 端：从索引 0 开始
        idx_high = min(int(abs(random.gauss(0, n / 3))), n - 1)
        # 低 var 端：从索引 n-1 开始
        idx_low = max(n - 1 - int(abs(random.gauss(0, n / 3))), 0)

        # 避免同一张
        if idx_high == idx_low:
            idx_low = (idx_high + 1) % n

        def to_image(row):
            return Image(
                hash=row[0],
                path=row[1],
                rating=Rating.from_var(row[2], row[3]),
                match_count=row[4]
            )

        return to_image(rows[idx_high]), to_image(rows[idx_low])

    def update(self, winner: Image, loser: Image):
        """更新比赛结果"""
        new_winner, new_loser = match1v1(winner.rating, loser.rating)
        print("winner:", winner.path, "new Rating:", new_winner.mean , "new var:", new_winner.var)
        print("loser:", loser.path, "new Rating:", new_loser.mean, "new var:", new_loser.var)

        self.conn.execute('''
            UPDATE images 
            SET mean = ?, var = ?, match_count = match_count + 1 
            WHERE hash = ?
        ''', (new_winner.mean, new_winner.var, winner.hash))

        self.conn.execute('''
            UPDATE images 
            SET mean = ?, var = ?, match_count = match_count + 1 
            WHERE hash = ?
        ''', (new_loser.mean, new_loser.var, loser.hash))

        self.conn.commit()

    def delete(self, hash: str) -> bool:
        """删除，返回是否删除成功"""
        cursor = self.conn.execute('DELETE FROM images WHERE hash = ?', (hash,))
        self.conn.commit()
        return cursor.rowcount > 0

    def get_ranking(self) -> List[Image]:
        """按 mean 降序"""
        rows = self.conn.execute('''
            SELECT hash, path, mean, var, match_count 
            FROM images ORDER BY mean DESC
        ''').fetchall()

        return [
            Image(
                hash=row[0],
                path=row[1],
                rating=Rating.from_var(row[2], row[3]),
                match_count=row[4]
            )
            for row in rows
        ]

    def count(self) -> int:
        return self.conn.execute('SELECT COUNT(*) FROM images').fetchone()[0]

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()