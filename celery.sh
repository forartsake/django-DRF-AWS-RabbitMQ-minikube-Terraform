#!/bin/sh
celery -A pet_project.pet_celery worker -l info
