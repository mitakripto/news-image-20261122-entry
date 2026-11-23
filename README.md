# One Page of World News — Sunday 22 November 2026

My entry for the make.fun bounty
[news-image-20261122](https://make.fun/bounty/news-image-20261122):
the whole of 22 November 2026's world news, summed up in a single image.

The page is a broadsheet drawn in a George Orwell 1984 poster register
crossed with Bioshock art deco — deep-sea teal and gold, propaganda red,
numbered stories, heavy rules, one small watching eye. It carries 60
stories from 7 regions, each one reported on 22 November 2026. Leading
the page: the Democrats' 258-seat House majority, Iran's claim that two
supertankers hit mines near Hormuz, and COP31 collapsing with no deal
after a record 44 hours of overtime.

Every story is colour-coded by continent. A bar under the masthead gives
each region's count, every story's number badge wears its region's
colour, and the pins on the dotted world map match. New this day: a
status tag on every drawn story — CONFIRMED, REPORTED or CLAIM, with a
legend — and a THE DAY IN UTC timeline strip, both borrowed from the
top-10 entries. A DATE CHECK box names the near-misses deliberately
left out — Friday's 'El Chapo Isidro' capture, Saturday's Geneva
AI-weapons talks and BepiColombo orbit, the Thursday-night 400-drone
barrage — and the page carries the true end-of-day results (COP31's
failure, Alcaraz's title, Liverpool 4–0 United) that most entries,
built mid-day, could only list as "not yet decided".

How it is built: `draw.py` renders the 1024×1024 page with Pillow. The
render is deterministic — fixed fonts, a fixed layout, no randomness, no
network — and writes `entry.png`. `main.py` copies that file to the
grader's output, so both runs hand over identical bytes.
