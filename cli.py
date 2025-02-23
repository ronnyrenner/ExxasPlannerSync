import click
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

@click.group()
def cli():
    """Management commands for Exxas-Planner Sync"""
    pass

@cli.command()
@click.argument('username')
@click.argument('password')
def create_user(username, password):
    """Create a new user with the given username and password"""
    with app.app_context():
        if User.query.filter_by(username=username).first():
            click.echo(f"User {username} already exists")
            return
        
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo(f"Created user {username}")

if __name__ == '__main__':
    cli()
