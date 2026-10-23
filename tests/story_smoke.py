"""Smoke story for tests/smoke.sh. Run from a workdir made by setup.sh: python3 <kit>/tests/story_smoke.py"""
import os, sys
sys.path.insert(0, os.getcwd())  # carousel_kit.py and assets/ live in the workdir
from PIL import Image
from carousel_kit import render

Image.new("RGB", (600, 800), (255, 255, 255)).save("assets/smoke-tall.png")  # taller than wide, so it cannot grow past 700px: must trigger SMALL IMAGE

STORY = {"slug": "smoke", "slides": [
    ("cover", "cover", "Smoke test", {"line1": "Google", "line2": "changed it.", "standfirst": "A render check for every slide type the daily run uses.",
                                      "mark": "logo-google.png", "mark_h": 170}),
    ("process", "process", "How it works", {"headline": "Four steps to send it", "steps": [
        ("logo-xero.png", "Connect Xero", "Link your accounting software to HMRC."),
        ("file-text", "Keep records", "Record income and expenses as you go."),
        ("send", "Send updates", "Submit a quarterly update from your software."),
        ("calendar", "Meet deadlines", "Each update is due a month after the period ends.")]}),
    ("limits", "limits", "Limits", {"headline": "What it does not cover", "rows_top": 420, "rows": [
        ("logo-ico.png", "Data protection", "Personal data rules still apply to your records."),
        ("circle-alert", "Late filing", "Penalty points build up for each missed deadline."),
        ("info", "Other taxes", "VAT and corporation tax have their own rules."),
        ("users", "Partnerships", "Partners join later, on a date still to be set.")]}),
    ("source", "source", "Source", {"img": "smoke-tall", "headline": "From GOV.UK",
                                    "body": "A deliberately tall, narrow image so the renderer warns that it is too small to read.",
                                    "credit": "Source: smoke test image"}),
    ("bigfact", "bigfact", "Key fact", {"figure": "4", "statement": "updates a year, one each quarter.",
                                        "context": "Plus a final declaration after the tax year ends.",
                                        "facts": [("Starts", "April 2026"), ("Applies to", "Income over £50,000")]}),
    ("recap", "recap", "Recap", {"items": [("Sign up", "Check whether you need to join."), ("Pick software", "Choose a compatible product."),
                                          ("Send on time", "Four updates and one declaration.")]}),
    ("cta", "cta", "Benjo Builds", None),
]}

render(STORY)
