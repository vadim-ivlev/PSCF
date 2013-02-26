function Globals() {

//    this.SOVDEF_URL="/proxy/http://www.publicsectorcredit.org/SovDef/examples/full/datasource/demo.php?q=";
    this.SOVDEF_URL="/fiscal_data?iso=";
    this.SOVDEF_LOG_URL="/fiscal_data_log?id=";
    this.START_ISO="USA";
    this.COUNTRIES_URL="/countries";

    // to convert data to XLS
    var EXPORT_URL="http://www.publicsectorcredit.org/phpexcel/phpexcelfacade.php/?q=";

    this.commentWindow;  // window to enter comments to records

    /**
     * Loads HTML from url into a component
     * @param componentId
     * @param url
     */
    this.loadPage = function (componentId, url) {
        Ext.getCmp(componentId).loader.load(url);
    }

    /**
     * Serialise object into JSON string
     * @param o the object ti serialise
     * @return {*} Json string
     */
    this.getJson = function (o) {
        return Ext.JSON.encode(o);
    }

    /*
     * return GLOB.getCDATA(v, rec, this); show message in console
     */
    this.getCDATA=function(v,rec, thi)
    {
        return $(rec.raw).find("[name='"+thi.name+"']").text();
    }

    /**
     * show text in console if it exists
     * @param s
     */
    this.trace = function (s) {
        if (typeof (console) == "undefined") return;
        if (!console) return;
        console.log(s);
    }


    this.exportToExcel=function(){
        var iso=Ext.getCmp("cmbCountry").getValue();
        //window.open(EXPORT_URL+iso);
        window.open(this.SOVDEF_URL+iso+"&format=csv")
    }


    this.showCommentWindow=function(){
        //if (! this.commentWindow)
        this.commentWindow=Ext.create('MyApp.view.AddCommentWindow');
        this.commentWindow.show();
    }


    this.hideCommentWindow=function(){
        if (! this.commentWindow) return;
        this.commentWindow.close();
    }


    this.showTextOnTheCommentPanel=function(text){
        var commentPanel=Ext.getCmp("panelRecordComments");
        if (commentPanel.isHidden()) {
        } else {
            var commentContainer = Ext.getCmp("commentContainer");
            if (text==null || text=="")
            {
                commentContainer.el.dom.innerHTML ="";


            }
            else
            {
                commentContainer.el.dom.innerHTML = (""+text).replace(/\n/g,"<br>");

            }
            //commentContainer.doLayout();
            commentPanel.doLayout();

        }
       }


    this.getUserName=function(){
        var userEl=Ext.get("userName");
        if (! userEl || userEl.dom.innerHTML==="")
        {
            alert ("Log in to edit data.");
            return '';
        }
        return userEl.dom.innerHTML;
       /*
         var tip = Ext.create('Ext.tip.ToolTip', {
         //target: 'clearButton',
         showDelay:500,
         hideDelay:200,
         html: '<b>[Tab]</b> to move.  <b>[Enter]</b> to finish.'
         });

         tip.show();
         */
    }

    /**
     * returns currently selected record in the fiscal_data grid
     * @return {*} - selected record or null
     */
    this.getSelectedRecord=function(){
        var grid=Ext.getCmp("gridFiscalData");
        return grid.getSelectionModel().getLastSelected();
    }

    /**
     * returns currently selected record in the fiscal_data_log grid
     * @return {*} - selected record or null
     */
    this.getLogSelectedRecord=function(){
        var grid=Ext.getCmp("fiscalDataLogGrid");
        return grid.getSelectionModel().getLastSelected();
    }


    /**
     * called from line editor when the user hits save button.
     */
    this.saveChangesToFiscalData=function(){
        _scroll=getGridScroll("gridFiscalData");

        var record=this.getSelectedRecord();
        if (!record) return;
        record.raw['status']="pending";
        Ext.getStore("FiscalDataStore").sync({
            success:function(){
                setGridScroll("gridFiscalData",_scroll);
                this.refreshFiscalDataLogGrid();
            },
            failure: function(){},
            scope: this
        });
    }

    /**
     * Button handler for Add button on the comment panel
     */
    this.addCommentHandler = function(){
        var textInput=Ext.getCmp("newCommentTextArea");
        var commentText=textInput.getValue();
        this.addCommentToTheSelectedRecord(commentText,textInput);
    }

    /**
     * Adds a comment to the selected in the grid record and sends it to the server.
     * works independently from datastores.
     *
     * @param newCommentText -  a comment text to save
     * @param textInput - text input which needs to be cleaned after success.
     * @return {Boolean} - true if text was sent to the server.
     */
    this.addCommentToTheSelectedRecord = function(newCommentText, textInput){
        if (! newCommentText) return false;

        //Check if the user is logined in
        var userName=this.getUserName();
        if (! userName)  return false;

        //Get the record
        var record=this.getSelectedRecord();
        if (! record )
        {
            alert ("Please select a record first.");
            return false;
        }


        var oldText=record.raw.user_comment;//get("user_comment");
        var newCommentHTML=newCommentText.replace(/\n/g,"<br>");
        var text=oldText+"<br><hr>"+
            userName+"<br>"+
            this.getMysqlNowString()+"<br>"+
            newCommentHTML +"<br>";


        this.updateFiscalData( record.raw.iso, [{user_comment:text, id:record.raw.id}],
            function(){
                //color the line
                record.raw.user_comment=text;
                record.raw.status="pending";
                record.commit();

                //Change the text in comment panel
                GLOB.showTextOnTheCommentPanel(text);

                //erase text input
                if (textInput)
                    textInput.setValue("");

                GLOB.refreshFiscalDataLogGrid();

            },
            function(e){
                alert(e)
            }
        );

        return true;

    }


    /**
     * General function to update fiscal data.
     * Independant of datastores
     *
     * @param iso - iso (?)
     * @param params - a record to save in {id:12345, comment:"some comment" ...}
     * @param callback_success -  a function to call on success
     * @param callback_error - a function to call on error
     */
    this.updateFiscalData=function(iso, params, callback_success, callback_error)
    {
        Ext.Ajax.request({
            url:this.SOVDEF_URL+iso,
            method:"post",
            //params:params,
            jsonData:params,
            success:callback_success,
            failure:callback_error
        });
    }

    /**
     * General function to update fiscal data log table.
     * Independant of datastores
     *
     * @param params - a record to save in {log_id:12345, active:"yes" ...}
     * @param callback_success -  a function to call on success
     * @param callback_error - a function to call on error
     */
    this.updateFiscalDataLog=function(id, params, callback_success, callback_error)
    {
        Ext.Ajax.request({
            url:this.SOVDEF_LOG_URL+id,
            method:"post",
            jsonData:params,
            //params:params,
            success:callback_success,
            failure:callback_error
        });
    }




    /**
     * requests the server to get log records.
     * @param id -- id of the record to get log records
     */
    this.getFiscalDataLog = function(id){
        var store=Ext.getStore("LogStore");
        var proxy=store.getProxy();
        proxy.url=GLOB.SOVDEF_LOG_URL+id;
        store.load();
        this.trace("get log :"+id);
    }

    /**
     * works when the user chage selected record on the fiscal data grid
     */
    this.showFiscalDataLog = function(){
        //if log panel invisible exit
        if (Ext.getCmp("fiscalDataLogGrid").hidden) return;

        var record = this.getSelectedRecord();
        if (!record) return;

        this.getFiscalDataLog(record.raw.id);
    }

    var _showLogTimeout;
    /**
     * Calls showFiscalDataLog() after some interval of time.
     * To make requests to the sever less frequent.
     */
    this.showFiscalDataLogLater= function(){

        clearTimeout(_showLogTimeout);
        _showLogTimeout=setTimeout( "GLOB.showFiscalDataLog()",1000);
    }

    /**
     * adds custom editor subclass of a button as an edit renderer
     */
    this.addEditorsToFiscalData = function()
    {
        var userCommentsColumn=Ext.getCmp("userCommentsId");
        userCommentsColumn.setEditor(Ext.create('MyApp.view.CommentButton'));
    }

    this.launch=function(){
        //Ext.EventManager.on(window, 'beforeunload', this.saveState);
        //Ext.EventManager.on(window, 'unload',this.saveState );

        this.restoreState();

        var store=Ext.getStore("FiscalDataStore");
        //store.load({url:"/fiscal_data?iso=USA"});
        var proxy=store.getProxy();
        proxy.url=this.SOVDEF_URL+this.START_ISO;
        store.load();


        var store2=Ext.getStore("CountriesJsonStore");
        var proxy2=store2.getProxy();
        proxy2.url=this.COUNTRIES_URL;
        store2.load({
            callback: function(records, operation, success) {
                // the operation object
                // contains all of the details of the load operation
                Ext.getCmp("cmbCountry").setValue(GLOB.START_ISO);
           }
       });
       //this.addEditorsToFiscalData();
    }



    /**
     * Returns current date-time string in the same format as MySQL NOW() function
     * @return {String}
     */
    this.getMysqlNowString = function(){
        var d=new Date();
        var dateString=d.toISOString();
        dateString=dateString.replace("T"," ").replace(/\..*/,"");
        return dateString;
    }




    var _scroll;  //scroll position of fiscal_data grid
    var _log_scroll; // scroll position of fiscal_data_log grid

    /**
     * returns vertical scroll position of a grid
     * @param dataGridId - data grid id
     * @return {*}
     */
    function getGridScroll(dataGridId){
        var gridEl=Ext.getCmp(dataGridId).getEl();
        var viewEl=gridEl.down('.x-grid-view');
        var scroll=viewEl.getScroll();

        var grid=Ext.getCmp(dataGridId);
        var selRecord= grid.getSelectionModel().getLastSelected();
        if (selRecord)
            scroll.selectedIndex=selRecord.index;
        return scroll;
    }

    /**
     * Sets vertical scroll position of a grid
     * @param dataGridId - data grid id
     * @param scroll
     */
    function setGridScroll(dataGridId,scroll){
        var gridEl=Ext.getCmp(dataGridId).getEl();
        var viewEl=gridEl.down('.x-grid-view');
        viewEl.scrollTo('top',scroll.top, false);

        var grid=Ext.getCmp(dataGridId);
        var selectionModel= grid.getSelectionModel();
        //selectionModel.select([scroll.selectedRecord]);
        selectionModel.select(scroll.selectedIndex);

    }



    /**
     * refreshes the fiscal data grid by requesting the server
     */
    this.refreshFiscalDataGrid = function(){
        _scroll=getGridScroll("gridFiscalData");
        var store=Ext.getStore("FiscalDataStore");
        store.load({
            callback: function(){
                setGridScroll("gridFiscalData",_scroll);
            },
            scope: this
        });
    }


    /**
     * refreshes the fiscal data log grid by requesting the server
     */
    this.refreshFiscalDataLogGrid = function(){
        //panel can be invisible
        if (Ext.getCmp("fiscalDataLogGrid").hidden) return;

        _log_scroll=getGridScroll("fiscalDataLogGrid");

        var store=Ext.getStore("LogStore");

        if (store.getProxy().url)
        try{
        store.load({
            callback: function(records,operation, success){
                setGridScroll("fiscalDataLogGrid",_log_scroll);
             },
            scope: this
        });
        }
        catch(e){}
    }

    /**
     * Edit renderer of "active" column of the _log grid
     * @param value
     * @param metaData
     * @param record
     * @return {String}
     */
    this.getActiveRendererString=function(value, metaData, record){
        var sNo="<a class='nonactive-label' href='javascript:GLOB.activateLogRecord(); void(0);' >Activate</a>";
        var sYes="<span class='active-label'>Yes</span>";
        return (value=="no" ? sNo : sYes );
    }

    /**
     * Called from editor renderer of "active" column of  the _log grid.
     * @param record
     * @param store
     */
    this.activateLogRecord = function(record,store){
        if (this.getUserName()=='') return;

//        this.trace("activateLogRecord");
        var record=this.getLogSelectedRecord();
        if (! record) return;

        //update trough datastore. uncontrollable loss of scroll position
        //record.set("active", "yes");

        //color the line
        //does not work
        // we call refreshFiscalDataLogGrid after saving to do this
        record.raw.active="yes";
        record.commit(); //???

        this.updateFiscalDataLog(record.raw.id, [{active:"yes", log_id:record.raw.log_id}],
            function(){
                GLOB.refreshFiscalDataGrid();
                GLOB.refreshFiscalDataLogGrid(); //to refresh renderers
            },
            function(e){
                alert(e)
            }
        );
    }

    /**
     * Edit renderer of "status" column of the _log grid
     * @param value
     * @param metaData
     * @param record
     * @return {String}
     */
    this.getStatusRendererString= function (value, metaData, record){
        var val=record.get('status');
        if (!val) val=" ";
        var v=val.substr(0,1);
        var a = v=='a' ? 'selected':'';
        var p = v=='p' ? 'selected':'';
        var r = v=='r' ? 'selected':'';

        var s='<select class="addCommentButton" onchange="GLOB.setLogRecordStatus(this)">'+
            '<option value="approved" '+a+'>approved</option>'+
            '<option value="pending" '+p+'>pending</option>'+
            '<option value="rejected" '+r+'>rejected</option>'+
            '</select>';
        return s;
    }

    /**
     * Called from editor renderer of "status" column of the _log grid.
     * @param sel
     * @return {*}
     */
    this.setLogRecordStatus=function(sel){
        if (this.getUserName()=='') return null;

        var val = sel.options[sel.selectedIndex].value;
        var record=this.getLogSelectedRecord();
        if (! record) return;

        //record.set("status",val);

        //coloring
        record.raw.status=val;

        //this.updateLogRecord();

        //if we need to update the fiscal data grid
        var refreshMainGrid= (record.raw.active==="yes");

        this.updateFiscalDataLog(record.raw.id, [{status:val, log_id:record.raw.log_id}],
            function(a,b,c){
                GLOB.refreshFiscalDataLogGrid(); //to refresh renderers
                if (refreshMainGrid) GLOB.refreshFiscalDataGrid();
            },
            function(e){
                alert(e)
            }
        );



    }


    /**
     * For coloring rows.
     * Called form getRowClass functions of grids.
     * Returns class of a row.
     *
     * @param record
     * @return {*} class name of a row
     */
    this.getRowStatus=function(record){

        var status = record.raw.status; // record.get('status');
        if (status == "pending") return 'pending-row';
        else if (status=="rejected") return 'rejected-row';
        else return null;
    }

    /**
     * Saves state of UI when the user selects countru or show or hide
     * comments and history panes.
     */
    this.saveState = function(){
        if(typeof(Storage)=="undefined") return;
        localStorage.sovdefdata_state=this.getState();
    }

    /**
     * reads UI state from local storage.
     * Called from launch function.
     */
    this.restoreState = function(){
        if(typeof(Storage)=="undefined") return;
        this.setState(localStorage.sovdefdata_state);
    }

    /**
     * Returns GUI state as a json string
     * @return {*}
     */
    this.getState = function(){
        var o=new Object();
        o.iso=""+Ext.getCmp("cmbCountry").getValue();
        o.commentsHidden=Ext.getCmp("panelRecordComments").hidden;
        o.btnShowComments_text=Ext.getCmp("btnShowComments").getText();
        o.historyHidden=Ext.getCmp("fiscalDataLogGrid").hidden;
        o.btnShowHistory_text=Ext.getCmp("btnShowHistory").getText();
        var st=Ext.JSON.encode(o);
        return st;
    }


    /**
     * Restores UI state from json string
     * @param s
     */
    this.setState = function(s){
        if (! s) return;
        var o=Ext.JSON.decode(s);

        if (o.iso) this.START_ISO= o.iso;

        if (o.hasOwnProperty("commentsHidden"))
        {
            var comm=Ext.getCmp("panelRecordComments");
            if (o.commentsHidden) comm.hide();
            else comm.show();
        }

        if (o.hasOwnProperty("btnShowComments_text"))
        {
            Ext.getCmp("btnShowComments").setText (o.btnShowComments_text);
        }

        if (o.hasOwnProperty("historyHidden"))
        {
            var hist=Ext.getCmp("fiscalDataLogGrid");
            if (o.historyHidden) hist.hide();
            else hist.show();
        }

        if (o.hasOwnProperty("btnShowHistory_text"))
        {
            Ext.getCmp("btnShowHistory").setText (o.btnShowHistory_text);
        }


    }



    this.hideHistoryPanel=function(){
        Ext.getCmp("btnShowHistory").setText("Show audit trail");
        Ext.getCmp("fiscalDataLogGrid").hide();
        this.saveState();
    }

    this.hideCommentsPanel=function(){
        Ext.getCmp("btnShowComments").setText("Show comments");
        Ext.getCmp("panelRecordComments").hide();
        this.saveState();
    }

    /**
     * Clears both panels if they are visible
     */
    this.clearPanels = function(){
        this.showTextOnTheCommentPanel(" ");
        //if log panel invisible exit
        if (Ext.getCmp("fiscalDataLogGrid").hidden) return;
        //this.getFiscalDataLog(-1);
        var store=Ext.getStore("LogStore");
        store.removeAll();
    }


}


var GLOB = new Globals();



