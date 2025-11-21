"""adicionando cnh

Revision ID: 08c2c9d0ebb8
Revises: 304c50da2272
Create Date: 2025-11-21 11:21:25.411413

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '08c2c9d0ebb8'
down_revision = '304c50da2272'
branch_labels = None
depends_on = None


def upgrade():
    # Corrigido: não mexer em constraints sem nome no SQLite
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('cnh', sa.String(length=11), nullable=True))
        batch_op.create_unique_constraint(
            'uq_usuarios_cnh', ['cnh'])  # agora tem nome!


def downgrade():
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.drop_constraint('uq_usuarios_cnh', type_='unique')
        batch_op.drop_column('cnh')
