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
  // @@usergroup-usermembership?b_start:int=0&userid=
  var form = jQuery('form[action*="@@usergroup-usermembership"]', context);
  if(form.length){
    jQuery(form).eearewrite({
      attr: 'action',
      oldVal: '@@usergroup-usermembership',
      newVal: 'www/@@usergroup-usermembership'
    });
    console.log('Rewrite done');
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
      var action = jQuery(this).attr('action');
      var selfform = jQuery(this);
      if(action.indexOf('/www') !== -1){
        return;
      }

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
      var action = jQuery(this).attr('action');
      var selfform = jQuery(this);
      if(action.indexOf('/www') !== -1){
        return;
      }

      jQuery(selfform).eearewrite({
        attr: 'action',
        oldVal: selfform.attr('action'),
        newVal: selfform.attr('action') + '/www'
      });
    });
  }
};


/**
  Apply EEA Rewrite Rules on document ready
*/
jQuery(document).ready(function(){
  try{
    jQuery.eearewriterules(jQuery('body'));
  }catch(err){
    if(window.console){
      console.log(err);
    }
  }
});
