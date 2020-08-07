import React from "react";
import ListItem from "@material-ui/core/ListItem";
import ListItemIcon from "@material-ui/core/ListItemIcon";
import ListItemText from "@material-ui/core/ListItemText";

class AccountList extends React.Component {

    render() {
        var elements = [];
        var accounts = this.props.accounts;
        for(var i=0;i<accounts.length;i++){
            elements.push(
                <ListItem button key={i}>
                  <ListItemIcon>
                  </ListItemIcon>
                  <ListItemText primary={accounts[i]['account_name']} secondary={accounts[i]['balance']} />
                </ListItem>
            );
        }
        return (
            <div>
            {elements}
            </div>
        );
    }
}

export default AccountList;