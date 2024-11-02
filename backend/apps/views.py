from django.shortcuts import render
from environs import Env
import os


env = Env()
env.read_env()

print(env("SECRET_KEY"))


# Create your views here.
