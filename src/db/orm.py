from black import timezone
from sqlalchemy import BigInteger, String, ForeignKey, func
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column
from datetime import datetime, date

def get_current_datetime():
	dt = datetime.now(tz=timezone.utc)
	return dt.replace(microsecond=0, tzinfo=None)

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

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
	name: Mapped[str] = mapped_column(String(25))
	billing_start_date: Mapped[date] = mapped_column(default=date.today)
	billing_end_date: Mapped[date] = mapped_column(default=date.today)
	blocked: Mapped[bool] = mapped_column(default=False)


class TransactionORM(Base):
	__tablename__ = "transactions"

	id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
	user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
	amount: Mapped[int] = mapped_column()
	created_at: Mapped[date] = mapped_column(default=get_current_datetime, server_default=func.now())
	updated_at: Mapped[date] = mapped_column(default=get_current_datetime, server_default=func.now())


class MessageORM(Base):
	__tablename__ = "messages"

	id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
	recipient: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
	text: Mapped[str] = mapped_column(String(250))
	created_at: Mapped[date] = mapped_column(default=get_current_datetime, server_default=func.now())
	updated_at: Mapped[date] = mapped_column(default=get_current_datetime, server_default=func.now())


class RegistrationORM(Base):
	__tablename__ = "registration"

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
	name: Mapped[str] = mapped_column(String(25))
	requested_at: Mapped[datetime] = mapped_column(default=get_current_datetime, server_default=func.now())