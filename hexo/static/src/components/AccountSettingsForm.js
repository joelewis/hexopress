import React from 'react'
import Utils from '../utils'

class AccountSettingsForm extends React.Component {
    
    render() {
        console.log(this.props.settings)
        return (
            <div className="form-container">
                <form action="/settings/account/" method="POST" ref="form">
                    <div className="form-group">
                        <label className="form-label" >Choose your username</label>
                        <div className="input-group">
                            <span className="input-group-addon">hexopress.com/@</span>
                            <input 
                                className="form-input" 
                                defaultValue={Utils.unescapeHTML(this.props.settings.username)} 
                                name="username" 
                                type="text" 
                                placeholder={Utils.unescapeHTML(this.props.settings.username)} />
                        </div>
                        
                    </div>
                    <div className="form-group">
                        <label className="form-label" >Your name</label>
                        <input
                            className="form-input" 
                            name="name" 
                            defaultValue={Utils.unescapeHTML(this.props.settings.name)} 
                            type="text" 
                            placeholder="John Doe" />
                    </div>
                    <button className="btn btn-primary" type="submit">Update</button>
                </form>
            </div>
        )
    }
}

export default AccountSettingsForm