
from datetime import datetime

from models.item import GameItem


class User:
    def __init__(self, id: int, msg_id: int, diff: int):
        self.is_bot = False
        self.id: int = id
        self.message_id: int = msg_id
        self.difficulty: int = diff
        self.start_wait_at: datetime = datetime.now()
        self.choice: GameItem = GameItem(-1, 'def', {})

    def __str__(self) -> str:
        return f"User {self.id} msg {self.message_id} choice {self.choice} diff {self.difficulty}"

    def __repr__(self):
        return str(self)

class FakeUser(User):
    def __init__(self, *args):
        super().__init__(*args)
        self.is_bot = True