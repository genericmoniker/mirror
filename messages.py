import datetime
import json
from collections import namedtuple
from functools import partial

from flask import render_template, Flask, request
from pathlib import Path

import mail
from cache import Cache

MESSAGE_REFRESH_MINUTES = 5

Message = namedtuple('Message', 'template, context')

cache = None


def init_cache(app, scheduler):
    global cache
    cache = Cache(
        scheduler,
        'Refresh Messages',
        MESSAGE_REFRESH_MINUTES,
        partial(get_message_data, app),
    )


def get_message_data(app: Flask):
    messages = []
    now = datetime.datetime.now()
    if now.month == 12 and now.day in range(1, 26):
        messages.append(_get_ltw2017_message(app, now))
    messages.append(_get_52stories_message(app, now))
    messages.extend(_get_email_messages(app))
    return messages


def get_message():
    assert cache, 'init_cache must be called first!'
    messages = cache.get()
    request_message_number = int(request.args.get('n', 0))
    message_number = request_message_number % len(messages)
    message = messages[message_number]
    # It might be nice if we put the rendered template in the cache, but the
    # render_template function only works on a thread with a Flask app context.
    return render_template(message.template, **message.context)


def _get_ltw2017_message(app: Flask, now):
    data = _load_data(app, 'ltw2017', 'data.json')
    context = data[now.day - 1]
    return Message('ltw2017.html', context)


def _get_52stories_message(app: Flask, now: datetime):
    data = _load_data(app, '52stories', 'data.json')
    week_number = now.isocalendar()[1]
    context = data[week_number - 1]
    return Message('52stories.html', context)


def _get_email_messages(app: Flask):
    messages = mail.fetch_messages(app)
    return [Message('email.html', m) for m in messages]


def _load_data(app: Flask, *path_segments):
    data_file = Path(app.static_folder, *path_segments)
    with data_file.open('r', encoding='utf-8') as f:
        return json.load(f)


def light_the_world_data(now):
    title, content = (
        # Dec 1
        (
            'Jesus Lifted Others’ Burdens and So Can You',
            '<center>WORLDWIDE DAY OF SERVICE</center>'
        ),
        # Dec 2
        (
            'Jesus Honored His Parents and So Can You',
            """
            <ul>
                <li>Call (not text) your parents.</li>
                <li>Write a handwritten note to
                your parents or in-laws.</li>
                <li>Learn about an ancestor and
                share their story. For help, try
                    FamilySearch.org.</li>
            </ul>
            """
        ),
        # Dec 3
        (
            'Jesus Helped Others to See and So Can You',
            """
            <ul>
                <li>Find an eyeglasses collection box and donate an old
                pair.</li>
                <li>Point out a virtue in someone they don’t see in
                themselves.</li>
                <li>Promote a vision charity on social media. You could even
                use the eyeglasses emoji.</li>
            </ul>
            """
        ),
        # Dec 4
        (
            'Jesus Worshipped His Father and So Can You',
            """
            <ul>
                <li>Attend a church service in your area—you’re always invited
                to one of ours.</li>
                <li>Make a goal to offer a kneeling
                prayer to Heavenly Father
                every day in December.</li>
                <li>Help clean up or maintain a
                church building.</li>
            </ul>
            """
        ),
        # Dec 5
        (
            'Jesus Healed the Sick and So Can You',
            """
            <ul>
                <li>Sign up to be an organ donor.</li>
                <li>Give blood at your local blood
                bank.</li>
                <li>Resolve to pray daily for your
                loved ones who are sick or
                suffering.</li>
            </ul>
            """
        ),
        # Dec 6
        (
            'Jesus Read the Scriptures and So Can You',
            """
            <ul>
                <li>Set your alarm 15 minutes early
                for scripture study.
                </li>
                <li>Post your favorite scripture on
                social media.</li>
                <li>Text a scripture to someone
                who may need a boost.</li>
            </ul>
            """
        ),
        # Dec 7
        (
            'Jesus Fed the Hungry and So Can You',
            """
            <ul>
                <li>Donate non-perishable items
                to a local food bank.</li>
                <li>Invite a neighbor on a tight
                budget to dinner.</li>
                <li>Learn about satisfying spiritual
                hunger (start with John 6:35).</li>
            </ul>
            """
        ),
        # Dec 8
        (
            'Jesus Prayed for Others and So Can You',
            """
            <ul>
                <li>Think about a friend that’s going
                through some rough challenges.
                Say a prayer for them.</li>
                <li>Ask God how you can be an
                answer to someone else’s prayer.</li>
                <li>When was the last time you
                prayed with your family? How
                about right now?</li>
            </ul>
            """
        ),
        # Dec 9
        (
            'Jesus Visited the Lonely and So Can You',
            """
            <ul>
                <li>Visit a nursing home. Studies
                show 60% never get visitors
                during their stay.
                </li>
                <li>Invite a widow or widower to
                dinner.</li>
                <li>Identify someone that will be
                alone for Christmas. Invite
                them to attend a church service
                with you on Christmas Day.</li>
            </ul>
            """
        ),
        # Dec 10
        (
            'Jesus Helped People Walk and So Can You',
            """
            <ul>
                <li>Donate your old crutches,
                wheelchairs, or walkers to a
                group that refurbishes them.</li>
                <li>Plan an activity for a
                handicapped friend that’s
                catered to his/her capabilities. </li>
                <li>Offer to help an elderly person
                run errands.</li>
            </ul>
            """
        ),
        # Dec 11
        (
            'Jesus Ministered to Children and So Can You',
            """
            <ul>
                <li>Ask your children what they
                think you should pray about as
                a family.</li>
                <li>As a Christmas gift, purchase a
                picture of Jesus Christ for your
                child’s room. Teach your child
                of the Savior’s love for them.</li>
                <li>Make plans to take each of your
                children on a 1-on-1 activity.</li>
            </ul>
            """
        ),
        # Dec 12
        (
            'Jesus Taught Others and So Can You',
            """
            <ul>
                <li>Share your favorite teaching or
                story of Jesus on social media.</li>
                <li>Pass down something you
                learned from your parents or
                grandparents.</li>
                <li>Watch an online tutorial to
                learn a new skill that can
                benefit others.</li>
            </ul>
            """
        ),
        # Dec 13
        (
            'Jesus Showed Humility and So Can You',
            """
            <ul>
                <li>Share an experience with loved
                ones about a time you had to
                rely on God’s help.</li>
                <li>No matter your age, ask a
                parent how to deal with a
                current challenge in your life.</li>
                <li>Think of a time you were wrong
                about someone. Share it with a
                loved one.</li>
            </ul>
            """
        ),
        # Dec 14
        (
            'Jesus Taught Us to Clothe the Naked and So Can You',
            """
            <ul>
                <li>Collect winter clothing (old or
                new) for your local homeless
                shelter.</li>
                <li>Learn from a wise king how
                we should love those in need.
                (Mosiah 4:14-27)</li>
                <li>Recently bought some new
                clothes? Donate some old ones
                to a charity or thrift store.</li>
            </ul>
            """
        ),
        # Dec 15
        (
            'Jesus Worshipped through Song and So Can You',
            """
            <ul>
                <li>Invite a friend to attend a
                Christmas Day worship service
                to sing hymns and worship
                God.</li>
                <li>Share your favorite
                performance of a Christmas
                hymn on social media. </li>
                <li>Listen to Christmas hymns for
                an entire day.</li>
            </ul>
            """
        ),
        # Dec 16
        (
            'Jesus Showed Compassion and So Can You',
            """
            <ul>
                <li>Participate in a local sub-forSanta
                for a family that could
                use some holiday cheer.</li>
                <li>Try leaving only encouraging
                comments on social media.</li>
                <li>Pray for an opportunity today
                to show someone compassion.</li>
            </ul>
            """
        ),
        # Dec 17
        (
            'Jesus Cared for His Mother and So Can You',
            """
            <ul>
                <li>Call your mother right now.</li>
                <li>Make a list of all the things
                your mother has done for you.
                Send it to her. </li>
                <li>Identify a motherly figure in
                your life and take her flowers.</li>
            </ul>
            """
        ),
        # Dec 18
        (
            'Jesus Honored the Sabbath and So Can You',
            """
            <ul>
                <li>Turn off your phone for a few
                hours today. </li>
                <li>Attend a religious service in
                your area.</li>
                <li>Visit a family member.</li>
            </ul>
            """
        ),
        # Dec 19
        (
            'Jesus Calmed the Storm and So Can You',
            """
            <ul>
                <li>Learn ways you can help
                people around the world
                through charitable giving.</li>
                <li>Review emergency response
                plans for people living in your
                area.</li>
                <li>Give your family or loved ones
                the gift of a 72-hour kit for
                emergencies.</li>
            </ul>
            """
        ),
        # Dec 20
        (
            'Jesus Saw Potential in Others and So Can You',
            """
            <ul>
                <li>Be a mentor/tutor to someone. </li>
                <li>Take a child to work with you
                and let them do a small part of
                your job.</li>
                <li>Cheer someone on! Attend an
                event (athletic, cultural, etc.)
                to support someone you know.</li>
            </ul>
            """
        ),
        # Dec 21
        (
            'Jesus Forgave Others aand So Can You',
            """
            <ul>
                <li>Is there a family member you
                haven’t talked to lately? Call
                them.</li>
                <li>Make a list of your grudges.
                Then make plans to let them go. </li>
                <li>Be kind instead of right for an
                entire day.</li>
            </ul>
            """
        ),
        # Dec 22
        (
            'Jesus Showed Gratitude and So Can You',
            """
            <ul>
                <li>Give a simple gift to your mail
                carrier to raise spirits during
                their busiest season.</li>
                <li>Offer a prayer of pure
                gratitude. No requests. Just
                thanks.</li>
                <li>Write a thank you letter to
                someone who has positively
                impacted your life.</li>
            </ul>
            """
        ),
        # Dec 23
        (
            'Jesus was a Peacemaker and So Can You',
            """
            <ul>
                <li>Do you owe anyone an
                apology? Resolve to take
                action.</li>
                <li>Make a donation to help
                refugees from war-torn
                regions.</li>
                <li>Say nice things behind people’s
                backs today.</li>
            </ul>
            """
        ),
        # Dec 24
        (
            'Jesus Cared for His Loved Ones and So Can You',
            """
            <ul>
                <li>Plan a special Christmas Eve
                program with your family and
                friends.</li>
                <li>Leave an anonymous gift for a
                family member. </li>
                <li>Take a moment to enter all of
                your friends’ birthdays into
                your mobile device.</li>
            </ul>
            """
        ),
        # Dec 25
        (
            'Jesus’s Disciples Followed Him and So Can We',
            """
            <ul>
                <li>Turn some of the 25 Days ideas
                from this month into New
                Year’s resolutions. </li>
                <li>Find a picture of Jesus Christ
                that inspires you and place it in
                your home where it can serve as
                a reminder to follow Him. </li>
                <li>Have some time off? Devote
                one day to selfless service for
                those you love.</li>
            </ul>
            """
        ),
    )[now.day - 1]

    return dict(day=now.day, title=title, content=content)
