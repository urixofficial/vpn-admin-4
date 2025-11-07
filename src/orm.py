from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column
from datetime import date


class Base(DeclarativeBase):

	repr_cols_num = 2
	repr_cols = tuple()

	def __repr__(self):
		# cols = [f"{col}={getattr(self, col)}" for col in self.__table__.columns.keys()]
		cols = []
		for idx, col in enumerate(self.__table__.columns.keys()):
			if col in self.repr_cols or idx < self.repr_cols_num:
				cols.append(f"{col}={getattr(self, col)}")

		return f"<{self.__class__.__name__} {', '.join(cols)}>"

class UserORM(Base):
	__tablename__ = "users"

	id: Mapped[int] = mapped_column(primary_key=True)
	name: Mapped[str]
	billing_start_date: Mapped[date] = mapped_column(default=date.today)
	billing_end_date: Mapped[date] = mapped_column(default=date.today)
	blocked: Mapped[bool] = mapped_column(default=False)
