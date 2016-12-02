// From http://mormonwoman.org/2010/12/02/bible-and-book-of-mormon-scripture-advent/
var verses = [
    'Therefore the Lord himself shall give you a sign; Behold, a virgin shall conceive, and bear a son, and shall call his name Immanuel.',
    'And after the Messiah shall come there shall be signs given unto my people of his birth, and also of his death and resurrection; and great and terrible shall that day be unto the wicked, for they shall perish; and they perish because they cast out the prophets, and the saints, and stone them, and slay them; wherefore the cry of the eblood of the saints shall ascend up to God from the ground against them.',
    'And great multitudes came unto him, having with them those that were lame, blind, dumb, maimed, and many others, and cast them down at Jesus’ feet; and he healed them:',
    'Wherefore, he is the firstfruits unto God, inasmuch as he shall make intercession for all the children of men; and they that believe in him shall be saved.',
    'Behold, I am Jesus Christ, whom the prophets testified shall come into the world. And behold, I am the light and the life of the world; and I have drunk out of that bitter cup which the Father hath given me, and have glorified the Father in taking upon me the sins of the world, in the which I have suffered the will of the Father in all things from the beginning.',
    'And entering into the sepulchre, they saw a young man sitting on the right side, clothed in a long white garment; and they were affrighted.',
    'For he hath answered the ends of the law, and he claimeth all those who have faith in him; and they who have faith in him will cleave unto every good thing; wherefore he advocateth the cause of the children of men; and he welleth eternally in the heavens.',
    'Then said Jesus, Father, forgive them; for they know not what they do.',
    'And the world, because of their iniquity, shall judge him to be a thing of naught; wherefore they scourge him, and he suffereth it; and they smite him, and he suffereth it. Yea, they spit upon him, and he suffereth it, because of his loving kindness and his long-suffering towards the children of men.',
    'And he cometh into the world that he may save all men if they will hearken unto his voice; for behold, he suffereth the pains of all men, yea, the pains of every living creature, both men, women, and children, who belong to the family of Adam.',
    'And he commanded the multitude to sit down on the grass, and took the five loaves, and the two fishes, and looking up to heaven, he blessed, and brake, and gave the loaves to his disciples, and the disciples to the multitude. And they that had eaten were about five thousand men, beside women and children.',
    'And it came to pass that the multitude went forth, and thrust their hands into his side, and did feel the prints of the nails in his hands and in his feet; and this they did do, going forth one by one until they had all gone forth, and did see with their eyes and did feel with their hands, and did know of a surety and did bear record, that it was he, of whom it was written by the prophets, that should come.',
    'A new commandment I give unto you, That ye love one another; as I have loved you, that ye also love one another.',
    'And the Messiah cometh in the fulness of time, that he may redeem the children of men from the fall.',
    'And Jesus went about all Galilee, teaching in their synagogues, and preaching the gospel of the kingdom, and healing all manner of sickness and all manner of disease among the people.',
    'And it came to pass, that after three days they found him in the temple, sitting in the midst of the doctors, both hearing them, and asking them questions. And all that heard him were astonished at his understanding and answers.',
    'And she shall bring forth a son, and thou shalt call his name JESUS: for he shall save his people from their sins.',
    'And behold, he said unto them: Behold, I give unto you a sign; for five years more cometh, and behold, then cometh the Son of God to redeem all those who shall believe on his name.',
    'And behold, there shall a new star arise, such an one as ye never have beheld; and this also shall be a sign unto you. And it shall come to pass that whosoever shall believe on the Son of God, the same shall have everlasting life.',
    'And this shall be a sign unto you; Ye shall find the babe wrapped in swaddling clothes, lying in a manger.',
];

$(document).ready(function() {
    updateVerse();
    setInterval(updateVerse, 60 * 60 * 1000);
});


function updateVerse() {
    var date = moment().date();
    var verse = verses[date % 24 - 1]
    $("#text").html(verse);
    var random = getRandomInt(1, 3);
    var imgSrc = $("#image").attr("src");
    var imgSrcNew = imgSrc.replace(/\d/, random);
    console.log(imgSrc + ' -> ' + imgSrcNew);
    $("#image").attr("src", imgSrcNew);
}


// Returns a random integer between min (included) and max (included)
function getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min;
}