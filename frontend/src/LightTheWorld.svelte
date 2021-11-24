<script>
  import { DateTime } from "luxon";
  import { onMount } from "svelte";

  const ONE_MINUTE = 60000;

  const startDay = DateTime.local(2021, 11, 30);

  const activities = [
    {
      title: "Freely Give",
      description:
        "Jesus gave freely. We can too. Visit a Giving Machine near you, or donate time or money to a charity doing good in your area. Post a link on social media so others can donate as well",
    },
    {
      title: "Let Your Love Shine",
      description:
        "Jesus expressed love for others. Share a “top 3 things I love about you” message with at least three people. Then tag them on social media and invite them to do the same.",
    },
    {
      title: "Wise Man’s Gift",
      description:
        "What wise man or woman has blessed your life? Share your love and appreciation.",
    },
    {
      title: "The Christ Child",
      description:
        "Jesus’s birth is a gift of love for all of us. Get together with friends or family to watch The Christ Child or share the link online.",
    },
    {
      title: "Love Thy Neighbor",
      description:
        "Jesus taught us the true definition of loving our neighbor. Have a conversation with a neighbor you don’t know well.",
    },
    {
      title: "Fast Relief",
      description:
        "Go without a meal or two, and donate the cost of those missed meals to a charity that feeds people in need. Learn more about the blessings of fasting—request a visit with missionaries at LightTheWorld.org.",
    },
    {
      title: "Magic Memory",
      description:
        "Find a picture of a special Christmas memory you shared with a friend or family member. Share it with your loved one along with a message about why they’re important to you.",
    },
    {
      title: "Health Caring",
      description:
        "Express love for someone who cared for you or a family member in the past year. ",
    },
    {
      title: "Full Attention",
      description:
        "Jesus loved people enough to give them His complete attention. Today, commit to putting your phone down whenever someone’s talking to you.",
    },
    {
      title: "Light the Family Tree",
      description:
        "Honor those who came before you. Take some time today to learn about an ancestor. Call a grandparent or try out a family history tool like FamilySearch.org, and share what you found with your relatives.",
    },
    {
      title: "Showtime",
      description:
        "Jesus had an amazing way of making others feel included. Find a Christmas concert, play, or other event in your area, and invite someone to attend with you.",
    },
    {
      title: "Recipe for Rejoicing",
      description:
        "Jesus connected with others over shared meals. Learn how to make a traditional Christmas recipe from a particular part of the world. Then share it with friends or family.",
    },
    {
      title: "Save a Seat",
      description:
        "Share the joy of Christ’s birth. Invite a friend or family member to join you in celebrating the Savior’s birth at a Sunday worship service. Visit LightTheWorld.org to find our church near you.",
    },
    {
      title: "The Gift of Prayer",
      description:
        "When we pray with love, the Christmas season becomes brighter. Today, kneel and offer a prayer to God. Make it a goal to pray every morning this week. Need a little help getting started? You can learn more about how to pray at Become.org.",
    },
    {
      title: "Season’s Greetings",
      description:
        "Jesus reached out to the people around Him. Say hi to someone new today.",
    },
    {
      title: "Shining Star",
      description:
        "Dedicate the star on your tree to someone who was a light in your life this year. Take a picture and post it on social media along with a message about how that person has influenced you.",
    },
    {
      title: "Christmas Dinners",
      description:
        "Just like Jesus, you can feed the hungry. Drop off food to someone who could use it, or create a donation package for a local food bank. Recruit a friend to help.",
    },
    {
      title: "Secret Shepherd",
      description:
        "Who has been a shepherd for you, lovingly guiding you through life? Highlight them privately or publicly.",
    },
    {
      title: "Songs Worth Sharing",
      description:
        "Jesus and His followers received strength as they sang hymns together. Experience the power of sacred music—whether by singing with loved ones, caroling for neighbors, or sharing a performance of your favorite hymn with your social network.",
    },
    {
      title: "From Luke 2 You",
      description:
        "Remind yourself of the true reason for the season by reading a few passages of the Christmas story from Luke 2 in the Holy Bible. Visit LightTheWorld.org to hear a Christmas message from our missionaries.",
    },
    {
      title: "Together Time",
      description:
        "This Christmas, surround yourself with loved ones. Invite as many family members as you can to get together for a virtual hangout.",
    },
    {
      title: "Sharing Light",
      description:
        "Like Jesus, you can teach through stories. Share an inspirational story from your life that could help someone in your social network.",
    },
    {
      title: "Gifts from God",
      description:
        "You can express gratitude like Jesus did. Reflect on the gifts God has given you, and write them down. Share your gratitude with others.",
    },
    {
      title: "Treats Times Two",
      description:
        "Turn one good deed into two. Make two plates of treats. Drop one off to a friend; then give the other to someone your friend suggests.",
    },
    {
      title: "Love Mom and Dad",
      description:
        "Be like Jesus and express love for your parents (or a parental figure in your life). Call them, visit them, or post about them on social media.",
    },
    {
      title: "Jesus Is the Light of the World",
      description:
        "Share a scripture that you think demonstrates the reason for the Christmas season. Need some suggestions? Check out these Bible verses: John 3:16; Acts 4:10–12.",
    },
    {
      title: "Light 2022",
      description:
        "Keep sharing the love of Jesus Christ. Turn the challenge to #LightTheWorld every day into a New Year’s resolution. Don’t be afraid to share your goal with your social network.",
    },
  ];

  let activityIndex = calculateActivityIndex();

  $: valid = activityIndex >= 0;
  $: activity = valid
    ? activities[activityIndex]
    : { title: "", description: "" };

  function calculateActivityIndex() {
    let now = DateTime.local();
    let daysSinceStart = Math.floor(now.diff(startDay).as("days"));
    if (daysSinceStart >= 0 && daysSinceStart < activities.length) {
      return daysSinceStart;
    }
    return -1;
  }

  onMount(() => {
    const interval = setInterval(() => {
      let newIndex = calculateActivityIndex();
      if (newIndex !== activityIndex) {
        activityIndex = newIndex;
        console.log("Light the World index changed to: " + activityIndex);
      }
    }, ONE_MINUTE);

    return () => {
      clearInterval(interval);
    };
  });
</script>

<div>
  <p class="large">
    <img src="/images/ltw2021.svg" width="250px" alt="Light the World" />
    &nbsp;&nbsp;{activity.title}
  </p>
  <p class="narrow">{activity.description}</p>
</div>

<style>
  p {
    text-align: center;
  }

  img {
    vertical-align: middle;
  }

  .narrow {
    width: 50%;
    margin-left: auto;
    margin-right: auto;
  }
</style>
