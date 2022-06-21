(function() {
  'use strict';
  /* colormap.directive.js */

  /**
   * @desc Diretiva colormap
   * @example <div colormap></div>
   */
  var mod = angular.module('shared.widgets', []);

  mod.directive('colorMap', ['$http', colormap]);

  function colormap($http) {
    var directive = {
      link: link,
      templateUrl: 'public/app/shared/colormap.html',
      restrict: 'EA',
      controller: ['$scope', '$http', '$mdDialog', '$timeout', colormapCtrl],
      scope: {
        'change': '&',
        colormap: '=colormap'
      },
    };
    return directive;


    function link(scope, element, attrs) {}


    function colormapCtrl($scope, $http, $mdDialog, $timeout) {
      if (!_.isEmpty($scope.colorMaps)) return;
      $http.get('/cmaps').success(function(data) { $scope.colorMaps = data; })

      $scope.showColormap = function(ev) {
        $mdDialog.show({
          controller: DialogController,
          templateUrl: 'dialog1.tmpl.html',
          clickOutsideToClose: true,
          fullscreen: true
        })
      };

      $scope.delayChange = function() {
        $timeout(function() {
          $scope.change();
        });
      }

      function DialogController($scope, $mdDialog) {
        $scope.cancel = function() {
          $mdDialog.cancel();
        };
      }


    }

  }

})();
