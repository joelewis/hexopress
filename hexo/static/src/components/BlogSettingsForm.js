import React from 'react'
import Utils from '../utils'

class BlogSettingsForm extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            updated: false
        }
    }

    render() {
        return (
            <div className="form-container">
                <form action="/settings/blog/" method="POST" ref="form">
                    <div className="form-group form-group-hexopress">
                        <label className="form-label" >Blog Title</label>
                        <input 
                            className="form-input" 
                            defaultValue={Utils.unescapeHTML(this.props.settings.title)} 
                            name="title" 
                            type="text" 
                            placeholder="My Awesome Blog" />
                    </div>
                    <div className="form-group form-group-hexopress">
                        <label className="form-label" >Blog Subtitle</label>
                        <input 
                            className="form-input" 
                            name="subtitle" 
                            defaultValue={Utils.unescapeHTML(this.props.settings.subtitle)} 
                            type="text" 
                            placeholder="Random thoughts on code & philiosphy" />
                    </div>
                    <div className="form-group form-group-hexopress">
                        <label className="form-label" >A short description of the blog</label>
                        <textarea 
                            className="form-input" 
                            name="description" 
                            defaultValue={Utils.unescapeHTML(this.props.settings.description)} 
                            placeholder="A short description about you and the blog..." 
                            rows="3">
                        </textarea>
                    </div>
                    <button className="btn btn-primary" type="submit">Update</button>
                </form>
            </div>
        )
    }
}

export default BlogSettingsForm