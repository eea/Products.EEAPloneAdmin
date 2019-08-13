/**
  Rewrite some URLs as they work only on Plone Site while EEA apache points to
  an ATFolder called SITE
*/

/**
  EEA Rewrite Rule as a jQuery plugin
*/
jQuery.fn.eearewrite = function(options){
  var settings = {
    attr: 'href',
    oldVal: '',
    newVal: 'www'
  };

  return this.each(function(){

    var self = jQuery(this);

    if(options){
      jQuery.extend(settings, options);
    }

    var attr = self.attr(settings.attr);

    if(attr.indexOf(settings.newVal) !== -1 || attr.indexOf('/www/') !== -1){
      // Nothing to do, return
      return;
    }

    attr = attr.replace(settings.oldVal, settings.newVal);
    self.attr(settings.attr, attr);
  });
};

/**
  EEA Rewrite Rules
*/
jQuery.eearewriterules = function(context){

  var form;

  form = jQuery('form[action*="@@aliases-controlpanel"]', context);
  if(form.length){
    jQuery(form).eearewrite({
      attr: 'action',
      oldVal: '@@aliases-controlpanel',
      newVal: 'www/@@aliases-controlpanel'
    });
  }

  // @usergroup-userprefs
  form = jQuery('form[action*="@@usergroup-userprefs"]', context);
  if(form.length){
    jQuery(form).eearewrite({
      attr: 'action',
      oldVal: '@@usergroup-userprefs',
      newVal: 'www/@@usergroup-userprefs'
    });
  }

  form = jQuery('a[href*="@@usergroup-userprefs"]', context);
  if(form.length){
    jQuery(form).eearewrite({
      attr: 'href',
      oldVal: '@@usergroup-userprefs',
      newVal: 'www/@@usergroup-userprefs'
    });
  }

  form = jQuery('a[href*="@@usergroup-groupprefs"]', context);
  if(form.length){
    jQuery(form).eearewrite({
      attr: 'href',
      oldVal: '@@usergroup-groupprefs',
      newVal: 'www/@@usergroup-groupprefs'
    });
  }

  form = jQuery('a[href*="@@usergroup-controlpanel"]', context);
  if(form.length){
    jQuery(form).eearewrite({
      attr: 'href',
      oldVal: '@@usergroup-controlpanel',
      newVal: 'www/@@usergroup-controlpanel'
    });
  }

  form = jQuery('form[action*="@@eea-miniheader-controlpanel"]', context);
  if (form.length) {
    jQuery(form).eearewrite({
      attr: 'action',
      oldVal: '@@eea-miniheader-controlpanel',
      newVal: 'www/@@eea-miniheader-controlpanel'
    });
  }

  form = jQuery('a[href*="@@member-registration"]', context);
  if(form.length){
    jQuery(form).eearewrite({
      attr: 'href',
      oldVal: '@@member-registration',
      newVal: 'www/@@member-registration'
    });
  }

  form = jQuery('a[href*="@@overview-controlpanel"]', context);
  if(form.length){
    jQuery(form).eearewrite({
      attr: 'href',
      oldVal: '@@overview-controlpanel',
      newVal: 'www/@@overview-controlpanel'
    });
  }

  form = jQuery('a[href*="@@new-user"]', context);
  if(form.length){
    jQuery(form).eearewrite({
      attr: 'href',
      oldVal: '@@new-user',
      newVal: 'www/@@new-user'
    });
  }

  form = jQuery('form[action*="@@new-user"]', context);
  if(form.length){
    jQuery(form).eearewrite({
      attr: 'action',
      oldVal: '@@new-user',
      newVal: 'www/@@new-user'
    });
  }

  form = jQuery('a[href*="@@user-information"]', context);
  if(form.length){
    jQuery(form).eearewrite({
      attr: 'href',
      oldVal: '@@user-information',
      newVal: 'www/@@user-information'
    });
  }

  // @@usergroup-usermembership?b_start:int=0&userid=
  form = jQuery('form[action*="@@usergroup-usermembership"]', context);
  if(form.length){
    jQuery(form).eearewrite({
      attr: 'action',
      oldVal: '@@usergroup-usermembership',
      newVal: 'www/@@usergroup-usermembership'
    });
  }

  // @@usergroup-groupprefs
  form = jQuery('form[action*="@@usergroup-groupdetails"]', context);
  if(form.length){
    jQuery(form).eearewrite({
      attr: 'action',
      oldVal: '@@usergroup-groupdetails',
      newVal: 'www/@@usergroup-groupdetails'
    });
  }

  form = jQuery('form[action*="@@usergroup-groupprefs"]', context);
  if(form.length){
    jQuery(form).eearewrite({
      attr: 'action',
      oldVal: '@@usergroup-groupprefs',
      newVal: 'www/@@usergroup-groupprefs'
    });
  }

  // @@usergroup-groupmembership?groupname=
  form = jQuery('form[action*="@@usergroup-groupmembership"]', context);
  if(form.length){
    jQuery(form).eearewrite({
      attr: 'action',
      oldVal: '@@usergroup-groupmembership',
      newVal: 'www/@@usergroup-groupmembership'
    });
  }

  //@@manage-group-portlets?key=
  form = jQuery('form:has(input[value*="@@manage-group-portlets"])', context);
  if(form.length){
    jQuery.each(form, function(){
      var selfform = jQuery(this),
          action = selfform.attr('action'),
          new_action = action;

      if(action.substring(action.length - 4) !== '/www'){
        new_action = action + '/www';
      }

      jQuery(selfform).eearewrite({
        attr: 'action',
        oldVal: action,
        newVal: new_action
      });
    });
  }

  // @@manage-group-dashboard?key=
  form = jQuery('form:has(input[value*="@@manage-group-dashboard"])', context);
  if(form.length){
    jQuery.each(form, function(){
      var selfform = jQuery(this),
          action = selfform.attr('action'),
          new_action = action;

      if (action.substring(action.length - 4) !== '/www') {
        new_action = action + '/www';
      }

      jQuery(selfform).eearewrite({
        attr: 'action',
        oldVal: action,
        newVal: new_action
      });
    });
  }

  // @@types-controlpanel
  form = jQuery('form[action*="@@types-controlpanel"]', context);
  if(form.length){
    jQuery(form).eearewrite({
      attr: 'action',
      oldVal: '@@types-controlpanel',
      newVal: 'www/@@types-controlpanel'
    });
  }

  // @@manage-content-type-portlets
  form = jQuery('a[href*="@@manage-content-type-portlets"]', context);
  if(form.length){
    jQuery(form).eearewrite({
      attr: 'href',
      oldVal: '@@manage-content-type-portlets',
      newVal: 'www/@@manage-content-type-portlets'
    });
  }

  form = jQuery('form:has(input[value*="@@manage-content-type-portlets"])', context);
  if(form.length){
    jQuery.each(form, function(){
      var selfform = jQuery(this),
          action = selfform.attr('action'),
          new_action = action;

      if((action.indexOf('++contenttypeportlets++') === -1) &&
        (action.substring(action.length - 4) !== '/www')){
        new_action = action + '/www';
      }

      jQuery(selfform).eearewrite({
        attr: 'action',
        oldVal: action,
        newVal: new_action
      });
    });
  }

  // @@rules-controlpanel
  form = jQuery('form[action*="@@rules-controlpanel"]', context);
  if(form.length){
    jQuery(form).eearewrite({
      attr: 'action',
      oldVal: '@@rules-controlpanel',
      newVal: 'www/@@rules-controlpanel'
    });
  }

  // @@rules-controlpanel
  form = jQuery('form[action*="+rule/plone.ContentRule"]', context);
  if(form.length){
    jQuery(form).eearewrite({
      attr: 'action',
      oldVal: '+rule/plone.ContentRule',
      newVal: 'www/+rule/plone.ContentRule'
    });

    links = jQuery('a', form);
    if(links.length){
      jQuery(links).eearewrite({
        attr: 'href',
        oldVal: '+rule/plone.ContentRule',
        newVal: 'www/+rule/plone.ContentRule'
      });
    }
  }

  // @@rules-controlpanel - enable, disable & deletes content rule
  rule_enable = jQuery('input[name*="form.button.EnableRule"]', context);
  rule_disable = jQuery('input[name*="form.button.DisableRule"]', context);
  rule_delete = jQuery('input[name*="form.button.DeleteRule"]', context);

  if(rule_enable.length){
    jQuery.each(rule_enable, function(){
        var selfenable = jQuery(this);
        jQuery(this).eearewrite({
          attr: 'data-url',
          oldVal: selfenable.attr('data-url'),
          newVal: selfenable.attr('data-url').replace('@@contentrule-enable', 'www/@@contentrule-enable')
        });
    });
  }
  if(rule_disable.length){
    jQuery.each(rule_disable, function(){
        var selfdisable = jQuery(this);
        jQuery(this).eearewrite({
          attr: 'data-url',
          oldVal: selfdisable.attr('data-url'),
          newVal: selfdisable.attr('data-url').replace('@@contentrule-disable', 'www/@@contentrule-disable')
        });
    });
  }
  if(rule_delete.length){
    jQuery.each(rule_delete, function(){
        var selfdelete = jQuery(this);
        jQuery(this).eearewrite({
          attr: 'data-url',
          oldVal: selfdelete.attr('data-url'),
          newVal: selfdelete.attr('data-url').replace('@@contentrule-delete', 'www/@@contentrule-delete')
        });
    });
  }

  // @@rules-controlpanel - add action
  form = jQuery('form[action*="+action"]', context);
  if(form.length && context_url.indexOf("++rule++rule")){
    jQuery.each(form, function(){
      var selfform = jQuery(form);
      jQuery(form).eearewrite({
        attr: 'action',
        oldVal: selfform.attr('action'),
        newVal: selfform.attr('action').replace('/++rule++rule', '/www/++rule++rule')
      });
    });
  }

  // @@rules-controlpanel - add condition
  form = jQuery('form[action*="+condition"]', context);
  if(form.length && context_url.indexOf("++rule++rule")){
    jQuery.each(form, function(){
      var selfform = jQuery(form);
      jQuery(form).eearewrite({
        attr: 'action',
        oldVal: selfform.attr('action'),
        newVal: selfform.attr('action').replace('/++rule++rule', '/www/++rule++rule')
      });
    });
  }

  // @@rules-controlpanel - @@manage-elements
  form = jQuery('form[action*="@@manage-elements"]', context);
  if(form.length && context_url.indexOf("++rule++rule")){
    jQuery.each(form, function(){
      var selfform = jQuery(form);
      jQuery(form).eearewrite({
        attr: 'action',
        oldVal: selfform.attr('action'),
        newVal: selfform.attr('action').replace('/++rule++rule', '/www/++rule++rule')
      });
    });
  }

  // ++contenttypeportlets++
  form = jQuery('a[href*="++contenttypeportlets++"]', context);
  if(form.length){
    jQuery.each(form, function(){
      var selfform = jQuery(this);
      var action = selfform.attr('href');
      jQuery(selfform).eearewrite({
        attr: 'href',
        oldVal: action,
        newVal: action.replace('++contenttypeportlets++', 'www/++contenttypeportlets++')
      });
    });
  }

  // ++groupdashboard++
  form = jQuery('a[href*="++groupdashboard++"]', context);
  if(form.length){
    jQuery.each(form, function(){
      var selfform = jQuery(this);
      var action = selfform.attr('href');
      jQuery(selfform).eearewrite({
        attr: 'href',
        oldVal: action,
        newVal: action.replace('++groupdashboard++', 'www/++groupdashboard++')
      });
    });
  }

  // portal_vocabularies
  form = jQuery('form[action*="portal_vocabularies"]', context);
  if(form.length && window.location.hostname != 'localhost'){
    jQuery.each(form, function(){
      var selfform = jQuery(this);
      var action = selfform.attr('action');
      jQuery(selfform).eearewrite({
        attr: 'action',
        oldVal: action,
        newVal: action.replace('portal_vocabularies', 'www/portal_vocabularies')
      });
    });
  }

  // @@ldap-controlpanel
  form = jQuery('form[action*="@@ldap-controlpanel"]', context);
  if(form.length){
    jQuery(form).eearewrite({
      attr: 'action',
      oldVal: '@@ldap-controlpanel',
      newVal: 'www/@@ldap-controlpanel'
    });
  }

  form = jQuery('form[action*="LdapProperty"]', context);
  if(form.length){
    jQuery(form).eearewrite({
      attr: 'action',
      oldVal: '+ldapschema/plone.LdapProperty',
      newVal: 'www/+ldapschema/plone.LdapProperty'
    });
  }

  form = jQuery('form[action*="LdapServer"]', context);
  if(form.length){
    jQuery(form).eearewrite({
      attr: 'action',
      oldVal: '+ldapserver/plone.LdapServer',
      newVal: 'www/+ldapserver/plone.LdapServer'
    });
  }

  // @@sparql-schedule-controlpanel
  form = jQuery('form[action*="@@sparql-schedule-controlpanel"]', context);
  if(form.length && window.location.hostname != 'localhost'){
    jQuery.each(form, function(){
      var selfform = jQuery(this);
      var action = selfform.attr('action');
      jQuery(selfform).eearewrite({
        attr: 'action',
        oldVal: action,
        newVal: action.replace('@@sparql-schedule-controlpanel', 'www/@@sparql-schedule-controlpanel')
      });
    });
  }

  // @@audit-local-roles
  form = jQuery('form[action*="www.eea.europa.eu/@@audit-local-roles"]', context);
  if(form.length){
    jQuery(form).eearewrite({
      attr: 'action',
      oldVal: '@@audit-local-roles',
      newVal: 'www/@@audit-local-roles'
    });
  }

  // @@workflowmanager-addaction
  form = jQuery('form[action*="@@workflowmanager-addaction"]', context);
  if(form.length){
    var action = form.attr('action');
    jQuery(form).eearewrite({
      attr: 'action',
      oldVal: action,
      newVal: action.replace('@@workflowmanager-addaction', 'www/@@workflowmanager-addaction')
    });
  }

  form = jQuery('a[href*="@@workflowmanager-addaction"]', context);
  if(form.length){
    var href = form.attr('href');
    jQuery(form).eearewrite({
      attr: 'href',
      oldVal: href,
      newVal: href.replace('@@workflowmanager-addaction', 'www/@@workflowmanager-addaction')
    });
  }

  // @@workflowmanager-add-new-state - se repeta
  form = jQuery('form[action*="@@workflowmanager-add-new-state"]', context);
  if(form.length){
    jQuery.each(form, function(){
      var selfform = jQuery(this);
      var action = selfform.attr('action');
      jQuery(selfform).eearewrite({
        attr: 'action',
        oldVal: action,
        newVal: action.replace('@@workflowmanager-add-new-state', 'www/@@workflowmanager-add-new-state')
      });
    });
  }

  form = jQuery('a[href*="@@workflowmanager-add-new-state"]', context);
  if(form.length){
    jQuery.each(form, function(){
      var selfform = jQuery(this);
      var href = selfform.attr('href');
      jQuery(selfform).eearewrite({
        attr: 'href',
        oldVal: href,
        newVal: href.replace('@@workflowmanager-add-new-state', 'www/@@workflowmanager-add-new-state')
      });
    });
  }

  // @@workflowmanager-add-new-transition - se repeta
  form = jQuery('form[action*="@@workflowmanager-add-new-transition"]', context);
  if(form.length){
    jQuery.each(form, function(){
      var selfform = jQuery(this);
      var action = selfform.attr('action');
      jQuery(selfform).eearewrite({
        attr: 'action',
        oldVal: action,
        newVal: action.replace('@@workflowmanager-add-new-transition', 'www/@@workflowmanager-add-new-transition')
      });
    });
  }

  form = jQuery('a[href*="@@workflowmanager-add-new-transition"]', context);
  if(form.length){
    jQuery.each(form, function(){
      var selfform = jQuery(this);
      var href = selfform.attr('href');
      jQuery(selfform).eearewrite({
        attr: 'href',
        oldVal: href,
        newVal: href.replace('@@workflowmanager-add-new-transition', 'www/@@workflowmanager-add-new-transition')
      });
    });
  }

  // @@workflowmanager-add-new-workflow
  form = jQuery('form[action*="@@workflowmanager-add-new-workflow"]', context);
  if(form.length){
    jQuery.each(form, function(){
      var selfform = jQuery(this);
      var action = selfform.attr('action');
      jQuery(selfform).eearewrite({
        attr: 'action',
        oldVal: action,
        newVal: action.replace('@@workflowmanager-add-new-workflow', 'www/@@workflowmanager-add-new-workflow')
      });
    });
  }

  form = jQuery('a[href*="@@workflowmanager-add-new-workflow"]', context);
  if(form.length){
    var href = form.attr('href');
    jQuery(form).eearewrite({
      attr: 'href',
      oldVal: href,
      newVal: href.replace('@@workflowmanager-add-new-workflow', 'www/@@workflowmanager-add-new-workflow')
    });
  }

  // @@workflowmanager-assign
  form = jQuery('form[action*="@@workflowmanager-assign"]', context);
  if(form.length){
    jQuery.each(form, function(){
      var selfform = jQuery(this);
      var action = selfform.attr('action');
      jQuery(selfform).eearewrite({
        attr: 'action',
        oldVal: action,
        newVal: action.replace('@@workflowmanager-assign', 'www/@@workflowmanager-assign')
      });
    });
  }

  form = jQuery('a[href*="@@workflowmanager-assign"]', context);
  if(form.length){
    var href = form.attr('href');
    jQuery(form).eearewrite({
      attr: 'href',
      oldVal: href,
      newVal: href.replace('@@workflowmanager-assign', 'www/@@workflowmanager-assign')
    });
  }

  // @@workflowmanager-view-graph
  form = jQuery('form[action*="@@workflowmanager-view-graph"]', context);
  if(form.length){
    var action = form.attr('action');
    jQuery(form).eearewrite({
      attr: 'action',
      oldVal: action,
      newVal: action.replace('@@workflowmanager-view-graph', 'www/@@workflowmanager-view-graph')
    });
  }

  form = jQuery('a[href*="@@workflowmanager-view-graph"]', context);
  if(form.length){
    jQuery.each(form, function(){
      var selfform = jQuery(this);
      var href = selfform.attr('href');
      jQuery(selfform).eearewrite({
        attr: 'href',
        oldVal: href,
        newVal: href.replace('@@workflowmanager-view-graph', 'www/@@workflowmanager-view-graph')
      });
    });
  }

  form = jQuery('img[src*="@@workflowmanager-view-graph"]', context);
  if(form.length){
    var src = form.attr('src');
    jQuery(form).eearewrite({
      attr: 'src',
      oldVal: src,
      newVal: src.replace('@@workflowmanager-view-graph', 'www/@@workflowmanager-view-graph')
    });
  }

  // @@workflowmanager-delete-workflow - se repeta
  form = jQuery('form[action*="@@workflowmanager-delete-workflow"]', context);
  if(form.length){
    jQuery.each(form, function(){
      var selfform = jQuery(this);
      var action = selfform.attr('action');
      jQuery(selfform).eearewrite({
        attr: 'action',
        oldVal: action,
        newVal: action.replace('@@workflowmanager-delete-workflow', 'www/@@workflowmanager-delete-workflow')
      });
    });
  }

  form = jQuery('a[href*="@@workflowmanager-delete-workflow"]', context);
  if(form.length){
    var href = form.attr('href');
    jQuery(form).eearewrite({
      attr: 'href',
      oldVal: href,
      newVal: href.replace('@@workflowmanager-delete-workflow', 'www/@@workflowmanager-delete-workflow')
    });
  }

  // @@workflowmanager-deleteaction
  form = jQuery('form[action*="@@workflowmanager-deleteaction"]', context);
  if(form.length){
    var action = form.attr('action');
    jQuery(form).eearewrite({
      attr: 'action',
      oldVal: action,
      newVal: action.replace('@@workflowmanager-deleteaction', 'www/@@workflowmanager-deleteaction')
    });
  }

  form = jQuery('a[href*="@@workflowmanager-deleteaction"]', context);
  if(form.length){
    jQuery.each(form, function(){
      var selfform = jQuery(this);
      var href = selfform.attr('href');
      jQuery(selfform).eearewrite({
        attr: 'href',
        oldVal: href,
        newVal: href.replace('@@workflowmanager-deleteaction', 'www/@@workflowmanager-deleteaction')
      });
    });
  }

  // @@workflowmanager-delete-state
  form = jQuery('form[action*="@@workflowmanager-delete-state"]', context);
  if(form.length){
    jQuery.each(form, function(){
      var selfform = jQuery(this);
      var action = selfform.attr('action');
      jQuery(selfform).eearewrite({
        attr: 'action',
        oldVal: action,
        newVal: action.replace('@@workflowmanager-delete-state', 'www/@@workflowmanager-delete-state')
      });
    });
  }

  form = jQuery('a[href*="@@workflowmanager-delete-state"]', context);
  if(form.length){
    jQuery.each(form, function(){
      var selfform = jQuery(this);
      var href = selfform.attr('href');
      jQuery(selfform).eearewrite({
        attr: 'href',
        oldVal: href,
        newVal: href.replace('@@workflowmanager-delete-state', 'www/@@workflowmanager-delete-state')
      });
    });
  }

  // @@workflowmanager-delete-transition
  form = jQuery('form[action*="@@workflowmanager-delete-transition"]', context);
  if(form.length){
    jQuery.each(form, function(){
      var selfform = jQuery(this);
      var action = selfform.attr('action');
      jQuery(selfform).eearewrite({
        attr: 'action',
        oldVal: action,
        newVal: action.replace('@@workflowmanager-delete-transition', 'www/@@workflowmanager-delete-transition')
      });
    });
  }

  form = jQuery('a[href*="@@workflowmanager-delete-transition"]', context);
  if(form.length){
    jQuery.each(form, function(){
      var selfform = jQuery(this);
      var href = selfform.attr('href');
      jQuery(selfform).eearewrite({
        attr: 'href',
        oldVal: href,
        newVal: href.replace('@@workflowmanager-delete-transition', 'www/@@workflowmanager-delete-transition')
      });
    });
  }

  // @@workflowmanager-update-security-settings
  form = jQuery('form[action*="@@workflowmanager-update-security-settings"]', context);
  if(form.length){
    jQuery.each(form, function(){
      var selfform = jQuery(this);
      var action = selfform.attr('action');
      jQuery(selfform).eearewrite({
        attr: 'action',
        oldVal: action,
        newVal: action.replace('@@workflowmanager-update-security-settings', 'www/@@workflowmanager-update-security-settings')
      });
    });
  }

  form = jQuery('a[href*="@@workflowmanager-update-security-settings"]', context);
  if(form.length){
    var href = form.attr('href');
    jQuery(form).eearewrite({
      attr: 'href',
      oldVal: href,
      newVal: href.replace('@@workflowmanager-update-security-settings', 'www/@@workflowmanager-update-security-settings')
    });
  }

  // @@workflowmanager-save-state
  form = jQuery('form[action*="@@workflowmanager-save-state"]', context);
  if(form.length){
    jQuery.each(form, function(){
      var selfform = jQuery(this);
      var action = selfform.attr('action');
      jQuery(selfform).eearewrite({
        attr: 'action',
        oldVal: action,
        newVal: action.replace('@@workflowmanager-save-state', 'www/@@workflowmanager-save-state')
      });
    });
  }

  // @@workflowmanager-save-transition
  form = jQuery('form[action*="@@workflowmanager-save-transition"]', context);
  if(form.length){
    jQuery.each(form, function(){
      var selfform = jQuery(this);
      var action = selfform.attr('action');
      jQuery(selfform).eearewrite({
        attr: 'action',
        oldVal: action,
        newVal: action.replace('@@workflowmanager-save-transition', 'www/@@workflowmanager-save-transition')
      });
    });
  }

  // @@workflowmanager-save-graph
  form = jQuery('form[action*="@@workflowmanager-save-graph"]', context);
  if(form.length){
    var action = form.attr('action');
    jQuery(form).eearewrite({
      attr: 'action',
      oldVal: action,
      newVal: action.replace('@@workflowmanager-save-graph', 'www/@@workflowmanager-save-graph')
    });
  }

  // @@workflowmanager-sanity-check
  form = jQuery('form[action*="@@workflowmanager-sanity-check"]', context);
  if(form.length){
    var action = form.attr('action');
    jQuery(form).eearewrite({
      attr: 'action',
      oldVal: action,
      newVal: action.replace('@@workflowmanager-sanity-check', 'www/@@workflowmanager-sanity-check')
    });
  }

  form = jQuery('a[href*="@@workflowmanager-sanity-check"]', context);
  if(form.length){
    var href = form.attr('href');
    jQuery(form).eearewrite({
      attr: 'href',
      oldVal: href,
      newVal: href.replace('@@workflowmanager-sanity-check', 'www/@@workflowmanager-sanity-check')
    });
  }

  // @@workflowmanager-edit-state
  form = jQuery('a[href*="@@workflowmanager-edit-state"]', context);
  if(form.length){
    var href = form.attr('href');
    jQuery(form).eearewrite({
      attr: 'href',
      oldVal: href,
      newVal: href.replace('@@workflowmanager-edit-state', 'www/@@workflowmanager-edit-state')
    });
  }

  // @@workflowmanager-edit-transition
  form = jQuery('a[href*="@@workflowmanager-edit-transition"]', context);
  if(form.length){
    var href = form.attr('href');
    jQuery(form).eearewrite({
      attr: 'href',
      oldVal: href,
      newVal: href.replace('@@workflowmanager-edit-transition', 'www/@@workflowmanager-edit-transition')
    });
  }


/*
  //@@manage-portlets
  links = jQuery('a[href*="@@spm-move-portlet-down"]', context);
  if(links.length){
    jQuery.each(links, function(){
      var selflink = jQuery(this),
          href = selflink.attr('href'),
          new_href = href;

      if(href.startsWith('/www/SITE')){
        alert('/www/SITE');
        new_href = href.replace('/SITE', '');
        alert(new_href);
      }
      if(!href.startsWith('/www')){
        alert('Not /www');
        new_href = '/www/' + href;
        alert(new_href);
      }

      jQuery(selflink).eearewrite({
        attr: 'href',
        oldVal: href,
        newVal: new_href
      });
    });
  }
*/

};


/**
  Apply EEA Rewrite Rules on document ready
*/
jQuery(document).ready(function(){

  var form;
  var context = jQuery('body');

  /* Rewrite on document ready */
  try{
    jQuery.eearewriterules(context);
  }catch(err){
    if(window.console){
      console.log(err);
    }
  }

  /* Rewrite on events */
  // On AddGroupButton click
  try{
    form = jQuery('input[name="form.button.AddGroup"]', context);
    if(form.length){
      form.click(function(){
        // Add a timer to give ajax call time to finish
        jQuery(this).oneTime(5000, "rewrite", function(){
          jQuery.eearewriterules(jQuery('.pb-ajax', context));
        });
      });
    }
  }catch(err2){
    if(window.console){
      console.log(err2);
    }
  }

  /* Rewrite on events */
  // WorkflowManager On

  var state_btn, trans_btn, wflw_btn, sec_btn, delwflw_btn, edit_state_btn, edit_trans_btn;

  try{
    // Add new state button
    state_btn = jQuery('input[name="add-new-state-button"]', context);
    if(state_btn.length){
      state_btn.click(function(){
        // Add a timer to give ajax call time to finish
        jQuery(this).oneTime(5000, "rewrite", function(){
          jQuery.eearewriterules(jQuery('.pb-ajax', context));
        });
      });
    }

    // Add new transition button
    trans_btn = jQuery('input[name="add-new-transition-button"]', context);
    if(trans_btn.length){
      trans_btn.click(function(){
        // Add a timer to give ajax call time to finish
        jQuery(this).oneTime(5000, "rewrite", function(){
          jQuery.eearewriterules(jQuery('.pb-ajax', context));
        });
      });
    }

    // Assign workflow button
    wflw_btn = jQuery('input[name="assign-workflow"]', context);
    if(wflw_btn.length){
      wflw_btn.click(function(){
        // Add a timer to give ajax call time to finish
        jQuery(this).oneTime(5000, "rewrite", function(){
          jQuery.eearewriterules(jQuery('.pb-ajax', context));
        });
      });
    }

    // Update security button
    sec_btn = jQuery('input[name="update-security-settings"]', context);
    if(sec_btn.length){
      sec_btn.click(function(){
        // Add a timer to give ajax call time to finish
        jQuery(this).oneTime(5000, "rewrite", function(){
          jQuery.eearewriterules(jQuery('.pb-ajax', context));
        });
      });
    }

    // Delete workflow button
    delwflw_btn = jQuery('input[name="delete-workflow-button"]', context);
    if(delwflw_btn.length){
      delwflw_btn.click(function(){
        // Add a timer to give ajax call time to finish
        jQuery(this).oneTime(5000, "rewrite", function(){
          jQuery.eearewriterules(jQuery('.pb-ajax', context));
        });
      });
    }

    // Edit state button
    edit_state_btn = jQuery('input#plumb-state-edit', context);
    if(edit_state_btn.length){
      edit_state_btn.click(function(){
        // Add a timer to give ajax call time to finish
        jQuery(this).oneTime(50000, "rewrite", function(){
          jQuery.eearewriterules(jQuery('.pb-ajax', context));
        });
      });
    }

    // Edit transition button
    edit_trans_btn = jQuery('input#plumb-transition-edit', context);
    if(edit_trans_btn.length){
      edit_trans_btn.click(function(){
        // Add a timer to give ajax call time to finish
        jQuery(this).oneTime(50000, "rewrite", function(){
          jQuery.eearewriterules(jQuery('.pb-ajax', context));
        });
      });
    }

  }catch(err3){
    if(window.console){
      console.log(err3);
    }
  }

});
