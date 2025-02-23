#!/usr/bin/env python3
import os
import sys
import click
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def check_environment():
    """Verify the environment is properly configured"""
    required_vars = ['DATABASE_URL']
    missing = [var for var in required_vars if not os.environ.get(var)]
    if missing:
        click.echo(f"Error: Missing environment variables: {', '.join(missing)}")
        click.echo("Please ensure all required environment variables are set.")
        sys.exit(1)

@click.group()
def cli():
    """Management commands for Exxas-Planner Sync"""
    check_environment()

@cli.command()
@click.argument('username')
@click.argument('password')
def create_user(username, password):
    """Create a new user with the given username and password"""
    try:
        with app.app_context():
            if User.query.filter_by(username=username).first():
                click.echo(f"Error: User {username} already exists")
                return 1

            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            click.echo(f"Successfully created user: {username}")
            return 0
    except Exception as e:
        click.echo(f"Error creating user: {str(e)}")
        click.echo("Please ensure the database is accessible and properly configured.")
        return 1

@cli.command()
@click.argument('username')
def delete_user(username):
    """Delete an existing user"""
    try:
        with app.app_context():
            user = User.query.filter_by(username=username).first()
            if not user:
                click.echo(f"Error: User {username} not found")
                return 1

            db.session.delete(user)
            db.session.commit()
            click.echo(f"Successfully deleted user: {username}")
            return 0
    except Exception as e:
        click.echo(f"Error deleting user: {str(e)}")
        return 1

@cli.command()
def list_users():
    """List all users"""
    try:
        with app.app_context():
            users = User.query.all()
            if not users:
                click.echo("No users found")
                return 0

            click.echo("\nExisting users:")
            for user in users:
                click.echo(f"- {user.username}")
            return 0
    except Exception as e:
        click.echo(f"Error listing users: {str(e)}")
        return 1

if __name__ == '__main__':
    cli()