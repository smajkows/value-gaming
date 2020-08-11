import React from "react";
import ListItem from "@material-ui/core/ListItem";
import ListItemIcon from "@material-ui/core/ListItemIcon";
import ListItemText from "@material-ui/core/ListItemText";
import CurrencyFormat from "react-currency-format";
import PlaidUpdateLink from "./PlaidUpdateLink";

class AccountList extends React.Component {

    render() {
        var elements = [];
        var accounts = this.props.accounts;
        for(var i=0;i<accounts.length;i++){
            elements.push(
                <ListItem button key={i}>
                    {this.props.owned_accounts ?
                        <ListItemIcon>
                            {accounts[i]['plaid_valid'] ? (<h3 style={{color: "green"}}>Valid</h3>) : (
                                <PlaidUpdateLink item_id={accounts[i]['item_id']}/>)}
                        </ListItemIcon> : <ListItemIcon></ListItemIcon>
                    }
                  <ListItemText primary={accounts[i]['account_name']}
                                secondary={<CurrencyFormat value={accounts[i]['balance']} displayType={'text'}
                                                           thousandSeparator={true}
                                                           prefix={'$'} decimalScale={2}/>}/>
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