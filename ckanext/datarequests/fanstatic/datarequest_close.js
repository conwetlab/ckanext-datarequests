
jQuery(document).ready(function () {

  // On page load select the first circumstance option
  showCondition(jQuery('#field-close_circumstance').find(':selected').data('condition'))

  // On change check if the selected circumstance has a condition
  jQuery('#field-close_circumstance').change(function () {
    showCondition(jQuery('#field-close_circumstance').find(':selected').data('condition'));
  });

  // Show the elements for the selected condition
  function showCondition(condition) {
    jQuery('#field-condition').val(condition)
    clearConditionElements()

    if (condition === 'nominate_dataset') {
      jQuery('#field-accepted_dataset_id').parent().parent().show()
      jQuery('#field-approx_publishing_date').parent().parent().hide()
    }
    else if (condition === 'nominate_approximate_date') {
      jQuery('#field-accepted_dataset_id').parent().parent().hide()
      jQuery('#field-approx_publishing_date').parent().parent().show()
    }
    else {
      jQuery('#field-accepted_dataset_id').parent().parent().hide()
      jQuery('#field-approx_publishing_date').parent().parent().hide()
    }
  }

  function clearConditionElements() {
    jQuery('#field-accepted_dataset_id').val('')
    jQuery('#field-approx_publishing_date').val('')
  }

});