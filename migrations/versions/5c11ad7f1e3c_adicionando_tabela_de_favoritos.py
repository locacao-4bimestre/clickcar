"""Adicionando tabela de favoritos

Revision ID: 5c11ad7f1e3c
Revises: 08c2c9d0ebb8
Create Date: 2025-11-25 01:54:03.439505

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c11ad7f1e3c'
down_revision = '08c2c9d0ebb8'
branch_labels = None
depends_on = None


def upgrade():
    # COMENTE ESTAS LINHAS (coloque # na frente)
    # op.create_table('tabela_favoritos',
    #     sa.Column('user_id', sa.Integer(), nullable=False),
    #     sa.Column('veiculo_id', sa.Integer(), nullable=False),
    #     sa.ForeignKeyConstraint(['user_id'], ['usuarios.id'], ),
    #     sa.ForeignKeyConstraint(['veiculo_id'], ['veiculos.id'], ),
    #     sa.PrimaryKeyConstraint('user_id', 'veiculo_id')
    # )
    pass


def downgrade():
    # REMOVE A TABELA DE FAVORITOS
    op.drop_table('tabela_favoritos')