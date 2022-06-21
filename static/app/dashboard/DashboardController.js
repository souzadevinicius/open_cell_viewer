(function() {

  'use strict';

  var dashboardControllers = angular.module('dashboardControllers', []);
  dashboardControllers.controller('DashboardCtrl', [
    '$scope', '$http', '$mdDialog', '$timeout',
    function($scope, $http, $mdDialog, $timeout) {
      var vm = this;
      vm.detectionTypes = ['contour', 'circle']

      vm.colors = [
        { name: 'red', value: '(255, 0, 0)' }, //  #FF0000
        { name: 'yellow', value: '(255, 255, 0)' }, // #FFFF00	
        { name: 'violet', value: '(148, 0, 211)' }, // #9400D3
        { name: 'green', value: '(0, 255, 0)' }, // #00FF00	
        { name: 'blue', value: '(0, 0, 255)' }, // #0000FF	
        { name: 'indigo', value: '(75, 0, 130)' }, // #4B0082	
        { name: 'orange', value: '(255, 127, 0)' }, // #FF7F00	
      ]

      vm.uploadFile = function() {

        $timeout(function() {
          if (_.isEmpty(vm.file))
            return
          if (!window.FormData)
            throw new Error('Unsupported browser version');
          vm.uploadedImages = [];
          var clrs = [];
          var form = new window.FormData();
          var indexColor = 0;
          for (var index = 0, len = vm.file.length; index < len; index++) {
            var element = vm.file[index];
            vm.uploadedImages.push({ name: element.name, url: '/uploads/thumb/' + element.name + '_thumb.png' + new Date().getTime(), color: vm.colors[indexColor] })
            form.append("file[]", element);
            clrs.push(vm.colors[indexColor].value)
            indexColor = indexColor < 6 ? indexColor + 1 : 0;
          }
          form.append('colors', clrs)
          var uploadUrl = ''

          if (vm.detection == 'contour')
            uploadUrl = '/upload?cm=' + vm.cm + '&lt=' + vm.minThreshold + '&ht=' + vm.maxThreshold + '&d=' + vm.denoise + '&ni=' + vm.numberIter + '&mia=' + vm.minArea + '&maa=' + vm.maxArea + '&dm=' + vm.detection + '&crmk=' + vm.colorMask
          else if (vm.detection == 'circle')
            uploadUrl = '/upload?cm=' + vm.cm + '&lt=' + vm.minThreshold + '&ht=' + vm.maxThreshold + '&d=' + vm.denoise + '&md=' + vm.minDistance + '&mr=' + vm.minRadius + '&mar=' + vm.maxRadius + '&dm=' + vm.detection + '&crmk=' + vm.colorMask
            // $http.post(uploadUrl, form, {
            //   transformRequest: angular.identity,
            //   headers: { 'Content-Type': undefined },

          $http({
            url: uploadUrl,
            method: 'POST',
            data: form,
            headers: { 'Content-Type': undefined },
            transformRequest: angular.identity
          }).success(function(data) {
            vm.original = data.original + "?" + new Date().getTime();
            vm.segmentation = data.segmentation + "?" + new Date().getTime();
            vm.contour = data.contour + "?" + new Date().getTime();
            vm.results = data.props;
          }).error(function(err) {
            if (err.msg)
              alert(err.msg)
          })

          return;
        }, 0)

      }
    }
  ]);
})();