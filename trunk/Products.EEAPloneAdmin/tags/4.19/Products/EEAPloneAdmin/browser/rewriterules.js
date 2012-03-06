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
      var selfform = jQuery(this);
      jQuery(selfform).eearewrite({
        attr: 'action',
        oldVal: selfform.attr('action'),
        newVal: selfform.attr('action') + '/www'
      });
    });
  }

  // @@manage-group-dashboard?key=
  form = jQuery('form:has(input[value*="@@manage-group-dashboard"])', context);
  if(form.length){
    jQuery.each(form, function(){
      var selfform = jQuery(this);
      jQuery(selfform).eearewrite({
        attr: 'action',
        oldVal: selfform.attr('action'),
        newVal: selfform.attr('action') + '/www'
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
      var selfform = jQuery(this);
      jQuery(selfform).eearewrite({
        attr: 'action',
        oldVal: selfform.attr('action'),
        newVal: selfform.attr('action') + '/www'
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
  if(form.length){
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
