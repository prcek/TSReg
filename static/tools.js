
        function log() {
                var args = (arguments.length > 1) ? Array.prototype.join.call(arguments, " ") : arguments[0];
                try { 
                    console.log(args);
                return true;
                } catch(e) {  
    
                }
                return false;
        }


        TOOLS = {}


        TOOLS.stopEvent = function(e) {
            var e = e || window.event;
            if (e.stopPropagation){
                e.stopPropagation();
            } else { 
                e.cancelBubble = true;
            }
        }


        TOOLS.cancelDef = function(e) {
            var e = e || window.event;
            if(e.preventDefault) {
                e.preventDefault();
            } else {
                e.returnValue = false;
            }
        }


        TOOLS.addListener = function (elm,eType,func) {
            if (document.addEventListener) {
                if (window.opera && (elm == window)){
                    elm = document;
                }
                elm.addEventListener(eType,func,false);
            } else if (document.attachEvent) {
                elm.attachEvent('on'+eType,func);
            }
            
        }

        TOOLS.gEl = function(ids){
            if (typeof(ids) == "string") {
                return document.getElementById(ids);
            } else { return ids; }
        }


        TOOLS.getElementsByClass = function (searchClass,node,tag) {
            var classElements = [];
            var node = node || document;
            var tag = tag || "*";

            var els = node.getElementsByTagName(tag);
            var elsLen = els.length;
        
            var pattern = new RegExp("(^|\\s)"+searchClass+"(\\s|$)");
            for (var i = 0, j = 0; i < elsLen; i++) {
                    if (pattern.test(els[i].className)) {
                            classElements[j] = els[i];
                            j++;
                    }
            }
            return classElements;
        }
        TOOLS.setupConfirm = function (confirmClass, confirmFce) {
            var hrefs = TOOLS.getElementsByClass(confirmClass,null);
            for(var i = 0; i < hrefs.length; i++) {
                TOOLS.addListener(hrefs[i],"click",confirmFce);
            } 
        }
       
        TOOLS.confirmDel = function (e, elm) {
            if (!confirm("Opravdu smazat?")) {
               TOOLS.cancelDef(e);
               TOOLS.stopEvent(e);
            }
        }
        TOOLS.confirmKick = function (e, elm) {
            if (!confirm("Opravdu vyřadit/odmítnout?")) {
               TOOLS.cancelDef(e);
               TOOLS.stopEvent(e);
            }
        }

        TOOLS.selectAll = function (e, elm) {
            var selects = TOOLS.getElementsByClass('check-action', null, 'input'); 
            var me = TOOLS.gEl('select-all')
            checked = me.checked;

            for(var i = 0; i < selects.length; i++) {
                if (selects[i].disabled == false) {
                    selects[i].checked = checked;
                }
            }
            
        }

        TOOLS.selector = function(mark) {
            log('new selector for mark =', mark)
            this.mark = mark;
            this._select();
        }


        TOOLS.selector.prototype._select = function() {
            log('_select function -', this.mark);
        }

        TOOLS.bindSelect = function (mark, selectFce) {
            log('bindSelect')
            s1 = new TOOLS.selector('a');
            s2 = new TOOLS.selector('b');
/*            s1._select()
            s2._select() */

            if(TOOLS.gEl(mark)) {
                TOOLS.addListener(TOOLS.gEl(mark), 'click', selectFce);
            }
        }




