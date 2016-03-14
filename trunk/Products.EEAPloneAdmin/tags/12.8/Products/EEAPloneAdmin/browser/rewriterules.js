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

    if(attr.indexOf(settings.newVal) !== -1){
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

};


/**
  Apply EEA Rewrite Rules on document ready
*/
jQuery(document).ready(function(){

  var form;
  var context = jQuery('body');

  /* Rewrite on document ready
  */
  try{
    jQuery.eearewriterules(context);
  }catch(err){
    if(window.console){
      console.log(err);
    }
  }

  /* Rewrite on events
  */

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

});
