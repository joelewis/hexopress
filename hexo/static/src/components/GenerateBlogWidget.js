import React from 'react'
import socket from '../socket'
import Utils from '../utils'
import PubSub from 'pubsub-js'

class GenerateBlogWidget extends React.Component {
    constructor(props) {
        super(props)
        this.info = {
            just_generated: "Your blog has been generated. Next time you write a post in your google drive folder, come back here and hit 'Refresh blog' to sync.",
            generate: "Looks like you haven't started your blog yet.",
            refresh: "We've dropped a folder named 'hexopress' into your gdrive. Go ahead, write posts and save it under that folder. When you hit 'Refresh blog', those posts will show up in your blog.",
            inprogress_refresh: "Refreshing your blog...",
            inprogress_generate: "Generating your blog...",
            folder: "We will be dropping a folder named 'hexopress' into your drive. When you write a post, put the google doc inside this folder."
        }
        
        this.state = {
            initiated: false,
            progress: 0,
            showingFolderInfo: false,
            generated: window.hexopress.is_generated,
            info: this.info.refresh
        }

        // subscribe
        PubSub.subscribe('blog_generation_initiated', (e, data) => {
            this.setState({
                initiated: true,
                info: this.state.generated ? this.info.inprogress_refresh : this.info.inprogress_generate,
                progress: 20
            })
        })
        
        PubSub.subscribe('blog_generation_progress', (e, data) => {
            this.setState(function() {
                return {
                    progress: data.progress
                }
            })
            if (data.info) {
                this.setState({
                    info: data.info
                })
            }
        })
        
        PubSub.subscribe('blog_generation_folder_created', (e, data) => {
             this.setState({
                 showingFolderInfo: true
            })
        })
        
        PubSub.subscribe('blog_generated', (e, data) => {
            this.setState({
                generated: true,
                info: this.info.just_generated,
                progress: 100
            })
        })
        
        PubSub.subscribe('access_token_expired', this.reLogin)
    }

    componentDidMount() {
        socket.addEventListener('open', function() {
            // socket.trigger('fetch_blog_status', {})

            // Bad place to put this code. Must revisit.
            const searchParams = Utils.getSearchParams()
            if (searchParams && searchParams.task) {
                socket.trigger(searchParams.task, {})
            }
        })
    }

    reLogin() {
        window.location.href= '/login?task=generate_blog'
    }

    generateBlog() {
        if (this.state.progress > 0 && this.state.progress < 100) {
            // already in progress
            return;
        }
        this.setState({
            progress: 0
        })
        socket.trigger('generate_blog', {})
    }

    render() {
        return (
            <div className="card startblog-card">
                <div className="card-image">
                    {/*<img class="img-responsive" src="img/osx-el-capitan.jpg" title="" style="">*/}
                </div>
                <div className="card-header">
                    <div className="card-title">
                        <a 
                        className="hexopress-blog-link"
                        href={Utils.getHost() + '/@' + hexopress.user.username}
                        target="_blank">
                            {Utils.getHost()}/@{hexopress.user.username}
                        </a>
                    </div>
                </div>
                <div className="card-body">
                    {this.state.info}
                </div>
                <div className="card-footer">
                    <a href="#" 
                        onClick={this.generateBlog.bind(this)} 
                        className={"btn btn-primary " + ((this.state.progress > 0 && this.state.progress < 100) ? "disabled": "")}>
                        Refresh blog        
                    </a>
                </div>
                <div className="bar bar-sm blog-generate-progress">
                    <div className="bar-item" role="progressbar" aria-valuenow="80" style={{ width: this.state.progress+'%'}} aria-valuemin="0" aria-valuemax="100"></div>
                </div>
            </div>
        )
    }
}

export default GenerateBlogWidget