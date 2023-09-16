"""empty message

Revision ID: c337c92936d1
Revises: 
Create Date: 2021-08-29 23:43:21.250543

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c337c92936d1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('coupons',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=128), nullable=False),
    sa.Column('coupon_code', sa.String(length=128), nullable=False),
    sa.Column('coupon_type', sa.String(length=64), nullable=False),
    sa.Column('coupon_discount_percentage', sa.Integer(), nullable=True),
    sa.Column('coupon_hands_given', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('hand_history_upload',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=128), nullable=True),
    sa.Column('original_filename', sa.String(length=512), nullable=True),
    sa.Column('morphed_filename', sa.String(length=256), nullable=True),
    sa.Column('file_format', sa.String(length=64), nullable=True),
    sa.Column('upload_timestamp', sa.DateTime(), nullable=True),
    sa.Column('processing_time', sa.Integer(), nullable=True),
    sa.Column('number_of_hands', sa.Integer(), nullable=True),
    sa.Column('number_of_hands_processed', sa.Integer(), nullable=True),
    sa.Column('is_processed', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('last_login_info',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=256), nullable=True),
    sa.Column('login_timestamp', sa.DateTime(), nullable=True),
    sa.Column('session_key', sa.String(length=256), nullable=True),
    sa.Column('ip_address', sa.String(length=256), nullable=True),
    sa.Column('user_agent', sa.String(length=128), nullable=True),
    sa.Column('browser_fingerprint', sa.String(length=256), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('login_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=256), nullable=True),
    sa.Column('login_timestamp', sa.DateTime(), nullable=True),
    sa.Column('session_key', sa.String(length=256), nullable=True),
    sa.Column('ip_address', sa.String(length=256), nullable=True),
    sa.Column('user_agent', sa.String(length=128), nullable=True),
    sa.Column('browser_fingerprint', sa.String(length=256), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('purchase_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(length=128), nullable=True),
    sa.Column('payment_id', sa.String(length=256), nullable=True),
    sa.Column('payment_email', sa.String(length=128), nullable=True),
    sa.Column('payment_phone_number', sa.String(length=64), nullable=True),
    sa.Column('amount', sa.Numeric(), nullable=True),
    sa.Column('payment_time', sa.DateTime(), nullable=True),
    sa.Column('payment_currency', sa.String(length=64), nullable=True),
    sa.Column('coupon_used', sa.String(length=64), nullable=True),
    sa.Column('hands', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('email', sa.String(length=256), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('registration_timestamp', sa.DateTime(), nullable=False),
    sa.Column('registration_date', sa.DateTime(), nullable=False),
    sa.Column('is_admin', sa.Boolean(), nullable=False),
    sa.Column('is_confirmed', sa.Boolean(), nullable=False),
    sa.Column('confirmation_timestamp', sa.DateTime(), nullable=True),
    sa.Column('is_pro', sa.Boolean(), nullable=True),
    sa.Column('pro_validity', sa.DateTime(), nullable=True),
    sa.Column('disabled', sa.Boolean(), nullable=True),
    sa.Column('processing_balance', sa.Integer(), nullable=True),
    sa.Column('device_id', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_table('purchase_history')
    op.drop_table('login_history')
    op.drop_table('last_login_info')
    op.drop_table('hand_history_upload')
    op.drop_table('coupons')
    # ### end Alembic commands ###
