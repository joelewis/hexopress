import React from 'react'

const FaqPage = (props) => {
    return (
        <div>
            <div className="faq-question">
                <h5> I have a problem using HexoPress. What do I do? </h5>
                <p> Write to me: <a href="#">lewis.joe.18@gmail.com</a>. I'll try to be as useful as possible.</p>
            </div>

            <div className="faq-question">
                <h5> How can I trust HexoPress? How can I know for sure it isn't stealing data? </h5>
                <p> HexoPress is an open source project. That not only means anybody can make it better, but also that it's very transparent on what files it talks to.</p>
            </div>

            <div className="faq-question">
                <h5> Can I use HexoPress for my existing Octopress blog? </h5>
                <p> If enough people want this, I'd add that to the roadmap.</p>
            </div>
            <div className="faq-question">
                <h5>I haven't completed a blog post yet. How can I stop it from being published in the blog?</h5>
                <p>Do not put incomplete posts in the "hexopress" directory. Move it there only when you are sure it's ready. If you accidentally published the post, simply put that file out of the directory, come back here and refresh your blog.</p>
            </div>
        </div>
    )
}

export default FaqPage